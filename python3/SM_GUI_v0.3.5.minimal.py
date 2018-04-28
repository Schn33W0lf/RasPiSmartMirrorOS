#python3.X
from sys import version_info
from time import sleep, strftime
from base64 import encodebytes
from io import BytesIO
from random import randint
from requests import head
import PIL
from PIL import ImageTk
import os
import RPi.GPIO as IO
if version_info[0] == 2:
    from urllib2 import urlopen
    from Tkinter import *
else:
    from urllib.request import urlopen
    from tkinter import *
#tkutils
def createImg(window, name, url, method, resizeX=None, resizeY=None):
    if method == 'TK':
        window.name = PhotoImage(data=encodebytes(urlopen(url).read()))
    elif method == 'PIL':
        window.name = ImageTk.PhotoImage(PIL.Image.open(BytesIO(urlopen(url).read())).resize((resizeX, resizeY), PIL.Image.ANTIALIAS))
    return window.name
def searchImg(url1, url2, rangeMin, rangeMax, debugInfos=False, fillZero=True):
    statusCode = [300, 1]
    while (
        statusCode[0] != 200 and
        statusCode[0] != 201 and
        statusCode[0] != 202 and
        statusCode[0] != 203 and
        statusCode[0] != 204 and
        statusCode[0] != 205 and
        statusCode[0] != 206 and
        statusCode[0] != 207 and
        statusCode[0] != 208 and
        statusCode[0] != 226):
        url = randint(rangeMin, rangeMax)
        if url > 9:
            if url > 99:
                if url > 999:
                    url = ''+str(url)
                else:
                    url = '0'+str(url)
            else:
                url = '00'+str(url)
        else:
            url = '000'+str(url)
        url = url1+url+url2
        resp = head(url)
        statusCode[0] = resp.status_code
        if debugInfos == True:
            print('[DEBUG] Code: '+str(statusCode[0])+' | URL: '+url+' | Try: '+str(statusCode[1]))
        statusCode[1] += 1
    return url
def tick():
    timeNew = strftime('%H:%M:%S%n%A, %d.%m.%Y')
    if SmartMirrorGUI.settings[1] != timeNew:
        SmartMirrorGUI.clock.config(text=timeNew)
        SmartMirrorGUI.canvasTextTempCpu
        SmartMirrorGUI.settings[1] = timeNew
        timeCpu = list(strftime('%S'))[1]
        if timeCpu == '0' or timeCpu == '5':
            SmartMirrorGUI.canvas.itemconfigure(SmartMirrorGUI.canvasTextTempOutside, text=round(float(20149/1000), 1))     #####TEMPERATURE OUTSIDE
            SmartMirrorGUI.canvas.itemconfigure(SmartMirrorGUI.canvasTextTempInside, text=round(float(30459/1000), 1))      #####TEMPERATURE INSIDE
            SmartMirrorGUI.canvas.itemconfigure(SmartMirrorGUI.canvasTextTempCpu, text=round(float(open('/sys/class/thermal/thermal_zone0/temp').read())/1000, 1))
        timeWeather = strftime('%S')
        if timeWeather == '00':
            gpioAction(3)
    SmartMirrorGUI.clock.after(200, tick)
def toggleFullscreen(event):
    SmartMirrorGUI.configs[1] = not SmartMirrorGUI.configs[1]
    SmartMirrorGUI.attributes('-fullscreen', SmartMirrorGUI.configs[1])
    SmartMirrorGUI.canvas.configure(width=SmartMirrorGUI.width[int(not SmartMirrorGUI.configs[1])], height=SmartMirrorGUI.height[int(not SmartMirrorGUI.configs[1])])
    return 'break'
def exitGUI(event):
    SmartMirrorGUI.configs[1] = False
    SmartMirrorGUI.attributes('-fullscreen', False)
    SmartMirrorGUI.canvas.configure(width=SmartMirrorGUI.width[1], height=SmartMirrorGUI.height[1])
    print('[DEBUG] Exiting . . .')
    statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
    sleep(0.1)
    statusLed(1, debugInfos=SmartMirrorGUI.configs[9])
    sleep(0.1)
    statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
    sleep(0.25)
    statusLed(1, debugInfos=SmartMirrorGUI.configs[9])
    sleep(1)
    loadGpio('CLEAN', True, [2, 3, 4, 17, 27], True)
#gpioControl
def loadGpio(gpioMode=None, setwarnings=False, pins=[[]], exitProgramm=False):
    if gpioMode == 'BCM':
        IO.setmode(IO.BCM)
    elif gpioMode == 'BOARD':
        IO.setmode(IO.BOARD)
    if gpioMode == 'BCM' or gpioMode == 'BOARD':
        IO.setwarnings(setwarnings)
        for i in range(len(pins)):
            pin = pins[i]
            if pin[1] == 'IN':
                IO.setup(pin[0],IO.IN)
            elif pin[1] == 'OUT':
                IO.setup(pin[0],IO.OUT)
    elif gpioMode == 'CLEAN':
        IO.setwarnings(setwarnings)
        for i in range(len(pins)):
            IO.cleanup(pins[i])
##  Not Working...
##        if exitProgramm == True:
##            raise SystemExit
    elif gpioMode == None or gpioMode == '':
        print('[WARNING] Mode unset. use \'BCM\' or \'BOARD\' or \'UNLOAD\'! setting mode \'',gpioMode,'\' because it was the default value.')
    else:
        print('[ERROR] Invalid Mode. use \'BCM\' or \'BOARD\' or \'UNLOAD\'! setting mode \'',gpioMode,'\' because it was the default value.')
def statusLed(status=0, red=17, green=27, debugInfos=False):
    if IO.getmode() == IO.BCM or IO.getmode()  == IO.BOARD:
        if status == 0 or status == 'off' or status == 'OFF':
            if debugInfos == False:
                print('status: 0 / off   / OFF')
            IO.output([red, green],IO.LOW)
        elif status == 1 or status== 'green' or status == 'GRN':
            if debugInfos == False:
                print('status: 1 / green / GRN')
            IO.output(red,IO.LOW)
            IO.output(green, IO.HIGH)
        elif status == 2 or status == 'red' or status == 'RED':
            if debugInfos == False:
                print('status: 2 / red   / RED')
            IO.output(green,IO.LOW)
            IO.output(red, IO.HIGH)
        elif status == 3 or status == 'test' or status == 'TST':
            if debugInfos == False:
                print('status: 3 / test  / TST')
                print('[+ statusLED-Test]')
            i = 0
            for i in range(3):
                statusLed(i)
                i += 1
                sleep(1)
            i = 0
            statusLed(0)
            if debugInfos == False:
                print('[- statusLED-Test]')
#main
def relayToTkinter(channel):
    if channel == 2:
        SmartMirrorGUI.event_generate('<<B1>>', when='tail')
    elif channel == 3:
        SmartMirrorGUI.event_generate('<<B2>>', when='tail')
    elif channel == 4:
        SmartMirrorGUI.event_generate('<<B3>>', when='tail')
def gpioAction(switch):
    if switch == 1:
        statusLed(2, debugInfos=SmartMirrorGUI.configs[9]);
        SmartMirrorGUI.canvasImgCartoonUrl = searchImg('http://ruthe.de/cartoons/strip_', '.jpg',0 , 9999, SmartMirrorGUI.configs[8], True)
        SmartMirrorGUI.canvasImgCartoon = createImg(SmartMirrorGUI, 'canvasImgCartoon', SmartMirrorGUI.canvasImgCartoonUrl, 'PIL', round(SmartMirrorGUI.configs[6]), round(SmartMirrorGUI.configs[7]))
        SmartMirrorGUI.canvas.create_image(
            SmartMirrorGUI.winfo_screenwidth()/2,
            685,
            image=SmartMirrorGUI.canvasImgCartoon,
            anchor=CENTER
        )
        SmartMirrorGUI.canvas.itemconfigure(SmartMirrorGUI.canvasImgCartoonId, text=SmartMirrorGUI.canvasImgCartoonUrl.split('_')[1].split('.jpg')[0])
        statusLed(1, debugInfos=SmartMirrorGUI.configs[9]);
    elif switch == 2:
        print('[DEBUG] Shutting down . . .')
        statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
        sleep(0.1)
        statusLed(1, debugInfos=SmartMirrorGUI.configs[9])
        sleep(0.1)
        statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
        sleep(0.25)
        statusLed(1, debugInfos=SmartMirrorGUI.configs[9])
        sleep(1)
        statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
        #loadGpio('CLEAN', False, [2, 3, 4, 17, 27])
        os.system('shutdown 0')
    elif switch == 3:
        statusLed(2, debugInfos=SmartMirrorGUI.configs[9]);
        SmartMirrorGUI.canvasImgWeather = createImg(SmartMirrorGUI, 'canvasImgWeather', ('https://www.theweather.com/wimages/'+SmartMirrorGUI.configs[5]+'.png'), 'TK')
        SmartMirrorGUI.canvas.create_image(
            SmartMirrorGUI.winfo_screenwidth()/2,
            110,
            image=SmartMirrorGUI.canvasImgWeather,
            anchor=CENTER
        )
        statusLed(1, debugInfos=SmartMirrorGUI.configs[9]);
    else:
        print('[WARNING] Error with GPIO Pins')
loadGpio('BCM', False, [[2, 'IN'], [3, 'IN'], [4, 'IN'], [17, 'OUT'], [27, 'OUT']])
SmartMirrorGUI = Tk()
# [bool(maximised), bool(fullscreen), float(windowWidth(%)), float(windowHeight(%)), float(versionNr), str(weatherSource), float(cartoonWidth), float(cartoonHeight), bool(cartoonFeedback), bool(gpioFeedback)]
SmartMirrorGUI.configs = [False, True, 0.75, 0.75, 0.3, 'foto99e83cda40fd2d3cd0a4d11485dffca2', 425*0.9 , 596*0.9, True, False]
SmartMirrorGUI.settings = [True, 'Loading. . .']
statusLed(2, debugInfos=SmartMirrorGUI.configs[9])
SmartMirrorGUI.width = [SmartMirrorGUI.winfo_screenwidth(), SmartMirrorGUI.winfo_screenwidth()*SmartMirrorGUI.configs[2]]
SmartMirrorGUI.height = [SmartMirrorGUI.winfo_screenheight(), SmartMirrorGUI.winfo_screenheight()*SmartMirrorGUI.configs[3]]
SmartMirrorGUI.canvasSize = int(not SmartMirrorGUI.configs[1])
SmartMirrorGUI.bind('<F11>', toggleFullscreen)
SmartMirrorGUI.bind('<Escape>', exitGUI)
SmartMirrorGUI.title('SmartMirror v'+str(SmartMirrorGUI.configs[4])+' >> GUI')
SmartMirrorGUI.geometry(
    '%dx%d+%d+%d' % (
        SmartMirrorGUI.width[1],
        SmartMirrorGUI.height[1],
        (SmartMirrorGUI.winfo_screenwidth()/2-(SmartMirrorGUI.winfo_screenwidth()*SmartMirrorGUI.configs[2])/2),
        (SmartMirrorGUI.winfo_screenheight()/2-(SmartMirrorGUI.winfo_screenheight()*SmartMirrorGUI.configs[3])/2)
    )
)
SmartMirrorGUI.attributes(
    '-zoomed', SmartMirrorGUI.configs[0],
    '-fullscreen', SmartMirrorGUI.configs[1]
)
SmartMirrorGUI.canvas = Canvas(
    SmartMirrorGUI,
    bg='black',
    cursor='none',
    width=SmartMirrorGUI.width[SmartMirrorGUI.canvasSize],
    height=SmartMirrorGUI.height[SmartMirrorGUI.canvasSize],
    borderwidth=0,
    highlightthickness=0
)
SmartMirrorGUI.canvas.pack()
SmartMirrorGUI.canvasImgCartoonId = SmartMirrorGUI.canvas.create_text(
    round(SmartMirrorGUI.winfo_screenwidth()/2),
    685+round(SmartMirrorGUI.configs[7]/2)+20,
    fill='white',
    font=('Helvetica', 20),
    anchor=CENTER,
    text='Loading . . .',
    activefill='white'
)
gpioAction(3)
gpioAction(1)
statusLed(2, debugInfos=False);
SmartMirrorGUI.canvasTextTempOutside = SmartMirrorGUI.canvas.create_text(
    round(SmartMirrorGUI.winfo_screenwidth()/4),
    685+round(SmartMirrorGUI.configs[7]/2)+75,
    fill='white',
    font=('Helvetica', 20),
    anchor=CENTER,
    text=('$O','°C'),
    activefill='white'
)
SmartMirrorGUI.canvasTextTempInside = SmartMirrorGUI.canvas.create_text(
    round(SmartMirrorGUI.winfo_screenwidth()/4*2),
    685+round(SmartMirrorGUI.configs[7]/2)+75,
    fill='white',
    font=('Helvetica', 20),
    anchor=CENTER,
    text=('$I','°C'),
    activefill='white'
)
SmartMirrorGUI.canvasTextTempCpu = SmartMirrorGUI.canvas.create_text(
    round(SmartMirrorGUI.winfo_screenwidth()/4*3),
    685+round(SmartMirrorGUI.configs[7]/2)+75,
    fill='white',
    font=('Helvetica', 20),
    anchor=CENTER,
    text=('$CPU','°C'),
    activefill='white'
)
SmartMirrorGUI.clock = Label(
    SmartMirrorGUI,
    font=('Helvetica', 50),
    text='Loading. . .',
    fg='white',
    bg='black',
    cursor='none'
)
SmartMirrorGUI.clock.place(
    relx=0.5,
    y=310,
    anchor='center'
)
IO.add_event_detect(2, IO.RISING, callback=relayToTkinter, bouncetime=300)
IO.add_event_detect(3, IO.RISING, callback=relayToTkinter, bouncetime=300)
IO.add_event_detect(4, IO.RISING, callback=relayToTkinter, bouncetime=300)
SmartMirrorGUI.bind('<<B1>>', lambda event:gpioAction(1))
SmartMirrorGUI.bind('<<B2>>', lambda event:gpioAction(2))
SmartMirrorGUI.bind('<<B3>>', lambda event:gpioAction(3))
statusLed(1, debugInfos=False)
tick()
SmartMirrorGUI.mainloop()
