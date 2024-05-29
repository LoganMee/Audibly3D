from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def main():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    # volume.SetMasterVolumeLevel(-20.0, None)
    # print("volume.GetMasterVolumeLevel(): %s" % volume.GetMasterVolumeLevel())
    print("volume.GetChannelCount(): %s" % volume.GetChannelCount())
    #volume.SetChannelVolumeLevelScalar(0, 0.3, None) #Left Channel Set to 0.3
    #volume.SetChannelVolumeLevelScalar(1, 0.3, None) #Right Channel Set to 0.3

    for x in range (10):
        volume.SetChannelVolumeLevelScalar(0, x/10, None)
        print(f"volume.GetChannelCount(): 0,{x/10}")


if __name__ == "__main__":
    main()