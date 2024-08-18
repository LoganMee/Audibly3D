from tkinter import *
import math, time, threading
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


#mathmatical Functions
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
        self.root.title("3D Audio")
        self.root.geometry("275x400")
        self.root.resizable(False, False)
        
        self.mainFrame = Frame(self.root)
        self.mainFrame.grid(column=0, row=0, padx=10, pady=10)
        self.sideBar = Frame(self.root)
        self.sideBar.grid(column=0, row=1, padx=10, pady=10)

        self.setupAudio()

        self.mode = IntVar()
        self.orbitRunning = False

    
    #################### Subroutines ####################
    def setupAudio(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
        self.leftStartingVolume = self.volume.GetChannelVolumeLevelScalar(0)
        self.rightStartingVolume = self.volume.GetChannelVolumeLevelScalar(1)
    
    def onClosing(self):
        self.volume.SetChannelVolumeLevelScalar(0, self.leftStartingVolume, None)
        self.volume.SetChannelVolumeLevelScalar(1, self.rightStartingVolume, None)
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
            canvas.moveto(audioSource, newX - radius/2, newY - radius/2)
            self.volumeChange(newX, newY, canvasCentre)
    
    def clickMode(self, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth):
        canvas.bind('<B1-Motion>', lambda event:self.move(event, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
        canvas.bind('<Button-1>', lambda event:self.move(event, audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
    
    def disableClickMode(self, canvas):
        canvas.unbind('<B1-Motion>')
        canvas.unbind('<Button-1>')
    
    def orbitAudio(self, audioSource, radius, canvas, canvasCentre, orbitRadius):
        self.orbitRunning = True
        self.disableClickMode(canvas)
        angle = angleBetweenPoints2(canvasCentre[0], canvas.coords(audioSource)[0]+ radius/2, canvasCentre[1], canvas.coords(audioSource)[1]+ radius/2)
        #print("start angle:", angle)
        canvas.moveto(audioSource, canvasCentre[0] + math.cos(angle)*radius - radius/2, canvasCentre[1] + math.sin(angle)*radius - radius/2)

        while self.mode.get() == 1:
            angle += (1/72*math.pi)
            newX = canvasCentre[0] + (math.cos(angle) * orbitRadius)
            newY = canvasCentre[1] + (math.sin(angle) * orbitRadius)

            canvas.moveto(audioSource, newX - radius/2, newY - radius/2)
            self.volumeChange(newX, newY, canvasCentre)

            time.sleep(12/144)
        self.orbitRunning = False

    def volumeChange(self, newX, newY, canvasCentre):
        distance = distanceBetweenPoints(canvasCentre[0], canvasCentre[1], newX, newY)
        distanceScaled = distance/25
        if distanceScaled > 1:
            intensityMultiplier = 1/(distanceScaled**2)
        else:
            intensityMultiplier = 1

        angle = angleBetweenPoints(canvasCentre[0], newX, distance)

        #Old exponential functions
        #leftIntensity = ((((math.sin(angle-math.pi)/2)+0.5)/(3/2))+(1/3)) * intensityMultiplier #minimum audio level of 1/3
        #rightIntensity = ((((math.sin(angle)/2)+0.5)/(3/2))+(1/3)) * intensityMultiplier

        #New linear functions
        leftIntensity = ((((((angle/(math.pi/2))*-1)/2)+0.5)/(3/2))+(1/3)) * intensityMultiplier #minimum audio level of 1/3
        rightIntensity = (((((angle/(math.pi/2))/2)+0.5)/(3/2))+(1/3)) * intensityMultiplier

        #print(leftIntensity, rightIntensity)
        
        self.volume.SetChannelVolumeLevelScalar(0, leftIntensity, None) #Left Channel
        self.volume.SetChannelVolumeLevelScalar(1, rightIntensity, None) #Right Channel

    def createWidgets(self):
        #################### GUI ####################
        #Canvas for Audio Simulation Visualisation
        radius = 25
        canvasWidth = 250
        canvasHeight = 250
        canvasCentre = [canvasWidth/2, canvasHeight/2]

        canvas = Canvas(self.mainFrame, width=canvasWidth, height=canvasHeight, bg="white")
        head = canvas.create_oval(canvasCentre[0]-radius, canvasCentre[1]-radius, canvasCentre[0]+radius, canvasCentre[1]+radius, outline="black", fill="wheat", width=2)
        audioSource = canvas.create_oval(canvasCentre[0]-radius/2, canvasCentre[1]-radius*2, canvasCentre[0]+radius/2, canvasCentre[1]-radius, outline="black", fill="Grey", width=2)
        canvas.grid(column=0, row=0)

        self.clickMode(audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth)

        #Menu
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="Settings", command=self.createSettingsWidgets)

        #Modes
        def threadStart():
            if not self.orbitRunning:
                orbitThread = threading.Thread(target=self.orbitAudio, args=(audioSource, radius, canvas, canvasCentre, 25))
                orbitThread.daemon = True
                orbitThread.start()

        modesLabel = Label(self.sideBar, text="Modes:", width=15)
        clickModeButton = Radiobutton(
            self.sideBar,
            text="Click",
            variable=self.mode,
            value=0,
            indicator=0,
            background="light blue",
            width=15,
            command=lambda:self.clickMode(audioSource, radius, canvas, canvasCentre, canvasHeight, canvasWidth))
        orbitModeButton = Radiobutton(
            self.sideBar,
            text="Orbit",
            variable=self.mode,
            value=1,
            indicator=0,
            background="light blue",
            width=15,
            command=threadStart)
        modesLabel.grid(row=0, column=1, padx=10, pady=1)
        clickModeButton.grid(row=1, column=1, padx=10, pady=1)
        orbitModeButton.grid(row=2, column=1, padx=10, pady=1)



    ##### Settings Window ####
    def createSettingsWidgets(self):
        self.settingsWin = Toplevel(self.root)
        self.settingsWin.title("Settings")
        self.settingsWin.geometry("275x400")
    #Output Device Settings
        outputDeviceSettingsLabel = Label(self.settingsWin, text = "Output Device Settings:")
        outputDeviceSettingsLabel.config(bg="Gray", width=30)
        outputDeviceSettingsLabel.grid(column=0, row=0, columnspan=2)

        outputDeviceLabel = Label(self.settingsWin, text = f"Output Device: ---") #{self.devices.GetId()}"
        outputDeviceLabel.grid(column=0, row=1)
        
        refindOutputDeviceButton = Button(self.settingsWin, width=17, text="Refind Output Device", command=self.setupAudio)
        refindOutputDeviceButton.grid(column=0, row=2, columnspan=2, pady=5)
    #Orbit Settings
        orbitSettingsLabel = Label(self.settingsWin, text = "Orbit Mode Settings:")
        orbitSettingsLabel.config(bg="Gray", width=30)
        orbitSettingsLabel.grid(column=0, row=3, columnspan=2, pady=5)
        
        orbitRadiusLabel = Label(self.settingsWin, text = "Orbit Radius (Px):")
        orbitRadiusLabel.grid(column=0, row=4)
        orbitRadiusSlider = Scale(self.settingsWin, from_=25, to=100, orient=HORIZONTAL)
        orbitRadiusSlider.grid(column=1, row=4)

        orbitSpeedLabel = Label(self.settingsWin, text = "Orbit Radius (Px):")
        orbitSpeedLabel.grid(column=0, row=5)
        orbitSpeedSlider = Scale(self.settingsWin, from_=25, to=100, orient=HORIZONTAL)
        orbitSpeedSlider.grid(column=1, row=5)
        
        orbitDirectionLabel = Label(self.settingsWin, text = "Orbit Direction:")
        orbitDirectionLabel.grid(column=0, row=6)

        orbitRefreshRateLabel = Label(self.settingsWin, text = "Orbit Refresh Rate:")
        orbitRefreshRateLabel.grid(column=0, row=7)



def main():
    audioSys1 = Audio3DInterface()
    audioSys1.run()

main()