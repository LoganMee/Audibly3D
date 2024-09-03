import comtypes
from pycaw.pycaw import AudioUtilities, IMMDeviceEnumerator, EDataFlow, DEVICE_STATE
from pycaw.constants import CLSID_MMDeviceEnumerator

devices = []
deviceEnumerator = comtypes.CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER)
collection = deviceEnumerator.EnumAudioEndpoints(EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)

for i in range(collection.GetCount()):
    dev = collection.Item(i)
    devices.append(AudioUtilities.CreateDevice(dev))

for device in devices:
    print(device.FriendlyName)
    print(device.id)

currentDevice = AudioUtilities.GetSpeakers()
print(f"\n{currentDevice.GetId()}")