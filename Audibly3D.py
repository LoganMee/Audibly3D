from tkinter import *
import math, time, threading
import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator, EDataFlow, DEVICE_STATE
from pycaw.constants import CLSID_MMDeviceEnumerator
import os
dir = os.path.dirname(__file__)


#Mathmatical Functions
def distanceBetweenPoints(x1,y1,x2,y2):
    changeInX = x2 - x1
    changeInY = y2 - y1
    distance = math.sqrt(changeInX**2 + changeInY**2)
    return distance

def angleBetweenPoints(x1, x2, hypotenuse):
    if hypotenuse > 0:
        changeInX = x2 - x1
        angle = math.asin(changeInX/hypotenuse) #Gets angle in radians
        return angle
    else:
        return 0

def angleBetweenPoints2(x1, x2, y1, y2): #Uses atan2 to preserve directionality but doesnt work with values of 0
    changeInX = x2 - x1
    changeInY = y2 - y1
    angle = math.atan2(changeInY, changeInX) #Gets angle in radians
    return angle


class Audio3DInterface:

    def __init__(self):
        self.root = Tk()
        self.root.title("Audibly3D")
        self.root.geometry("275x430")
        self.root.resizable(False, False)
        self.root.iconbitmap(os.path.join(dir, "images\logoIcon.ico"))
        
        self.mainFrame = Frame(self.root)
        self.mainFrame.grid(column=0, row=0, padx=10, pady=10)
        self.sideBar = Frame(self.root)
        self.sideBar.grid(column=0, row=1, padx=10, pady=10)

        self.mode = IntVar()
        self.minLvl = IntVar()
        self.orbitDirection = IntVar()
        self.orbitSpeed = IntVar()
        self.orbitRadius = IntVar()
        self.refreshRate = IntVar()
        self.orbitRunning = False
        self.gifActive = True
        self.currentOutputDevice = StringVar()

        self.clockwise = PhotoImage(file=os.path.join(dir, "images/clockwise.png")).subsample(18,18)
        self.antiClockwise = PhotoImage(file=os.path.join(dir, "images/antiClockwise.png")).subsample(18,18)
        self.headImg = PhotoImage(file=os.path.join(dir, "images/topViewMan50.png"))
        self.audioSourceGif = PhotoImage(file=os.path.join(dir, "images/audioSourceGif.gif"))
        self.aSframeCount = 4
        self.aSframes = [PhotoImage(file=os.path.join(dir,"images/audioSourceGif.gif"), format = 'gif -index %i' %(i)) for i in range(self.aSframeCount)]

        self.settingsDictionary = {"minLvl": self.minLvl, "orbitDirection": self.orbitDirection, "orbitSpeed": self.orbitSpeed, "orbitRadius": self.orbitRadius, "refreshRate": self.refreshRate}

        self.setupAudio()
        self.loadSettings()

    
    #################### Subroutines ####################
    def setupAudio(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
        self.leftStartingVolume = self.volume.GetChannelVolumeLevelScalar(0)
        self.rightStartingVolume = self.volume.GetChannelVolumeLevelScalar(1)
        self.getCurrentOutputDeviceName()
    
    def getOutputDevices(self):
        deviceEnumerator = comtypes.CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER)
        collection = deviceEnumerator.EnumAudioEndpoints(EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)
        devices = []

        for i in range(collection.GetCount()):
            dev = collection.Item(i)
            devices.append(AudioUtilities.CreateDevice(dev))
        return devices
    
    def getCurrentOutputDeviceName(self):
        for device in self.getOutputDevices():
            if device.id == self.devices.GetId(): 
                self.currentOutputDevice.set(device.FriendlyName)

    def loadSettings(self):
        with open(os.path.relpath('settings\settings.txt', dir), 'r') as f:
            for setting in self.settingsDictionary.values():
                setting.set(int(f.readline().split(':')[1]))
    
    def saveSettings(self):
        with open(os.path.relpath('settings\settings.txt', dir), 'w') as f:
            for settingName, setting in self.settingsDictionary.items():
                f.write(f"{settingName}: {setting.get()}\n")

    def restoreDefaultSettings(self):
        with open(os.path.relpath('settings\defaultSettings.txt', dir), 'r') as default, open(os.path.relpath('settings\settings.txt', dir), 'w') as settings:
            for line in default:
                settings.write(line)
        self.loadSettings()
    
    def resetToStarting(self):
        self.volume.SetChannelVolumeLevelScalar(0, self.leftStartingVolume, None)
        self.volume.SetChannelVolumeLevelScalar(1, self.rightStartingVolume, None)
    
    def onClosing(self):
        self.resetToStarting()
        self.root.destroy()
    
    def run(self):
        self.createWidgets()
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.mainloop()
 
    #Canvas subroutines
    def move(self, event, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth):
        newX = event.x
        newY = event.y
        if 0 <= newX <= canvasWidth and 0 <= newY <= canvasHeight: #Stops audio source from being dragged outside canvas
            canvas.moveto(audioSource, newX - radius, newY - radius)
            self.volumeChange(newX, newY, canvasCentre)
    
    def clickMode(self, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth):
        canvas.bind('<B1-Motion>', lambda event:self.move(event, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
        canvas.bind('<Button-1>', lambda event:self.move(event, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
    
    def disableClickMode(self, canvas):
        canvas.unbind('<B1-Motion>')
        canvas.unbind('<Button-1>')
    
    def orbitAudio(self, audioSource, radius, canvas, canvasCentre):
        self.orbitRunning = True
        self.disableClickMode(canvas)
        angle = angleBetweenPoints2(canvasCentre[0], canvas.coords(audioSource)[0], canvasCentre[1], canvas.coords(audioSource)[1])
        #print("start angle:", angle)
        canvas.moveto(audioSource, canvasCentre[0] + math.cos(angle)*radius - radius, canvasCentre[1] + math.sin(angle)*radius - radius)

        while self.mode.get() == 1:
            angle += (1/6*math.pi/self.refreshRate.get()*self.orbitSpeed.get()*self.orbitDirection.get())
            newX = canvasCentre[0] + (math.cos(angle) * self.orbitRadius.get())
            newY = canvasCentre[1] + (math.sin(angle) * self.orbitRadius.get())

            canvas.moveto(audioSource, newX - radius, newY - radius)
            self.volumeChange(newX, newY, canvasCentre)

            time.sleep(1/self.refreshRate.get())
        self.orbitRunning = False

    def volumeChange(self, newX, newY, canvasCentre):
        distance = distanceBetweenPoints(canvasCentre[0], canvasCentre[1], newX, newY)
        distanceScaled = distance/25
        if distanceScaled > 1:
            intensityMultiplier = 1/(distanceScaled**2)
        else:
            intensityMultiplier = 1

        angle = angleBetweenPoints(canvasCentre[0], newX, distance)

        #Linear Audio Level Functions
        minLvlFraction =  self.minLvl.get()/100
        leftIntensity = ((((((angle/(math.pi/2))*-1)/2)+0.5)*(1-minLvlFraction))+minLvlFraction) * intensityMultiplier #minimum audio level of minLvlFraction
        rightIntensity = (((((angle/(math.pi/2))/2)+0.5)*(1-minLvlFraction))+minLvlFraction) * intensityMultiplier
        #print(leftIntensity, rightIntensity)
        
        self.volume.SetChannelVolumeLevelScalar(0, leftIntensity, None) #Left Channel
        self.volume.SetChannelVolumeLevelScalar(1, rightIntensity, None) #Right Channel
    
    def audioSourceAnimation(self, audioSource, canvas):
        while self.gifActive:
            for i in range(self.aSframeCount):
                canvas.itemconfig(audioSource, image=self.aSframes[i])
                time.sleep(1)


    def createWidgets(self):
        #################### GUI ####################
        #Canvas for Audio Simulation Visualisation
        radius = 25
        canvasWidth = 250
        canvasHeight = 250
        canvasCentre = [canvasWidth/2, canvasHeight/2]

        canvas = Canvas(self.mainFrame, width=canvasWidth, height=canvasHeight, bg="white")
        #head = canvas.create_oval(canvasCentre[0]-radius, canvasCentre[1]-radius, canvasCentre[0]+radius, canvasCentre[1]+radius, outline="black", fill="wheat", width=2)
        head = canvas.create_image(canvasCentre[0], canvasCentre[1], image=self.headImg, anchor=CENTER)
        #audioSource = canvas.create_oval(canvasCentre[0]-radius/2, canvasCentre[1]-radius*2, canvasCentre[0]+radius/2, canvasCentre[1]-radius, outline="black", fill="Grey", width=2)
        self.audioSource = canvas.create_image(canvasCentre[0], canvasCentre[1]-radius*2, image=self.audioSourceGif, anchor=CENTER)
        canvas.grid(column=0, row=0)

        sourceGifThread = threading.Thread(target=self.audioSourceAnimation, args=(self.audioSource, canvas))
        sourceGifThread.daemon = True
        sourceGifThread.start()

        self.clickMode(self.audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth)

        #Menu
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="Settings", command=self.createSettingsWidgets)

        #Modes
        def threadStart():
            if not self.orbitRunning:
                orbitThread = threading.Thread(target=self.orbitAudio, args=(self.audioSource, radius, canvas, canvasCentre))
                orbitThread.daemon = True
                orbitThread.start()

        modesLabel = Label(self.sideBar, text="Modes:", width=15)
        clickModeButton = Radiobutton(
            self.sideBar,
            text="Click",
            variable=self.mode,
            value=0,
            indicator=0,
            bg="light blue",
            width=15,
            command=lambda:self.clickMode(self.audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
        orbitModeButton = Radiobutton(
            self.sideBar,
            text="Orbit",
            variable=self.mode,
            value=1,
            indicator=0,
            bg="light blue",
            width=15,
            command=threadStart)
        modesLabel.grid(row=0, column=1, padx=10, pady=1)
        clickModeButton.grid(row=1, column=1, padx=10, pady=1)
        orbitModeButton.grid(row=2, column=1, padx=10, pady=1)



    ##### Settings Window #####
    def createSettingsWidgets(self):
        if not any(isinstance(x, Toplevel) for x in self.root.winfo_children()): #Only one topLevel window at a time
            self.settingsWin = Toplevel(self.root)
            self.settingsWin.title("Settings")
            self.settingsWin.geometry("225x430")
            self.settingsWin.resizable(False, False)
    #Output Device Settings
        outputDeviceSettingsLabel = Label(self.settingsWin, text="Output Device Settings:")
        outputDeviceSettingsLabel.config(bg="Gray", width=30)
        outputDeviceSettingsLabel.grid(column=0, row=0, columnspan=3)

        outputDeviceLabel = Label(self.settingsWin, textvariable=self.currentOutputDevice)
        outputDeviceLabel.grid(column=0, row=1, columnspan=3, pady=3)
        
        refindOutputDeviceButton = Button(self.settingsWin, width=17, text="Refind Output Device", command=lambda:[self.resetToStarting(), self.setupAudio()])
        refindOutputDeviceButton.grid(column=0, row=2, columnspan=3, pady=3)
    #Audio Settings
        audioSettingsLabel = Label(self.settingsWin, text="Audio Settings:")
        audioSettingsLabel.config(bg="Gray", width=30)
        audioSettingsLabel.grid(column=0, row=3, columnspan=3, pady=5)

        minLvlLabel = Label(self.settingsWin, text="Min Audio Level:")
        minLvlLabel.grid(column=0, row=4)
        minLvlSlider = Scale(self.settingsWin, from_=0, to=75, orient=HORIZONTAL, variable=self.minLvl)
        minLvlSlider.grid(column=1, row=4, columnspan=2)
    #Orbit Settings
        orbitSettingsLabel = Label(self.settingsWin, text="Orbit Mode Settings:")
        orbitSettingsLabel.config(bg="Gray", width=30)
        orbitSettingsLabel.grid(column=0, row=5, columnspan=3, pady=5)

        orbitDirectionLabel = Label(self.settingsWin, text="Orbit Direction:")
        orbitDirectionLabel.grid(column=0, row=6)
        clockwiseBtn = Radiobutton(self.settingsWin, image=self.clockwise, variable=self.orbitDirection, value=1, indicator=0)
        clockwiseBtn.grid(column=1, row=6)
        antiClockwiseBtn = Radiobutton(self.settingsWin, image=self.antiClockwise, variable=self.orbitDirection, value=-1, indicator=0)
        antiClockwiseBtn.grid(column=2, row=6)
        
        orbitSpeedLabel = Label(self.settingsWin, text="Orbit Speed:")
        orbitSpeedLabel.grid(column=0, row=7)
        orbitSpeedSlider = Scale(self.settingsWin, from_=1, to=10, orient=HORIZONTAL, variable=self.orbitSpeed)
        orbitSpeedSlider.grid(column=1, row=7, columnspan=2)
        
        orbitRadiusLabel = Label(self.settingsWin, text="Orbit Radius (Px):")
        orbitRadiusLabel.grid(column=0, row=8)
        orbitRadiusSlider = Scale(self.settingsWin, from_=25, to=100, orient=HORIZONTAL, variable=self.orbitRadius)
        orbitRadiusSlider.grid(column=1, row=8, columnspan=2)

        orbitRefreshRateLabel = Label(self.settingsWin, text="Orbit Refresh Rate:")
        orbitRefreshRateLabel.grid(column=0, row=9)
        orbitRefreshRateSlider = Scale(self.settingsWin, from_=5, to=20, orient=HORIZONTAL, variable=self.refreshRate)
        orbitRefreshRateSlider.grid(column=1, row=9, columnspan=2)
        refreshRateInfoLabel = Label(self.settingsWin, text="*Higher refresh rates are more taxing.\n A lower refresh rate is recommened\n for slower machines.")
        refreshRateInfoLabel.grid(column=0, row=10, columnspan=3)
    #Main Buttons
        restoreDefaultButton = Button(self.settingsWin, width=12, text="Restore Default", command=self.restoreDefaultSettings)
        restoreDefaultButton.grid(column=0, row=11)
        saveSettingsButton = Button(self.settingsWin, width=8, text="Save", bg="light blue", command=self.saveSettings)
        saveSettingsButton.grid(column=2, row=11)


def main():
    audioSys1 = Audio3DInterface()
    audioSys1.run()

main()