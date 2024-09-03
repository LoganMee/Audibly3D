import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IMMDeviceEnumerator, EDataFlow, DEVICE_STATE, IAudioEndpointVolume
from pycaw.constants import CLSID_MMDeviceEnumerator

# ZOWIE XL LCD (NVIDIA High Definition Audio)
# {0.0.0.00000000}.{2d3563b9-2f91-480c-b339-28777dca1479}
# Speakers (4- USB Audio Device)
# {0.0.0.00000000}.{9df9ecb5-ffc4-4023-ae1b-d4430670b227}
# Realtek Digital Output (Realtek(R) Audio)
# {0.0.0.00000000}.{ba257d5b-f757-4438-8b88-b043f9e1784b}
# VG270U P (NVIDIA High Definition Audio)
# {0.0.0.00000000}.{d42eb584-fa40-4622-b0f1-f1a64c4d67e2}

deviceEnumerator = comtypes.CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER)
def switchDevice(id):
    device = deviceEnumerator.GetDevice(id)
    print(device)

switchDevice("{0.0.0.00000000}.{d42eb584-fa40-4622-b0f1-f1a64c4d67e2}")

def setupAudio(self, id=None):
    if id is None:   
        self.devices = AudioUtilities.GetSpeakers()
    else:
        deviceEnumerator = comtypes.CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER)
        self.devices = deviceEnumerator.GetDevice(id)
    self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
    self.leftStartingVolume = self.volume.GetChannelVolumeLevelScalar(0)
    self.rightStartingVolume = self.volume.GetChannelVolumeLevelScalar(1)
