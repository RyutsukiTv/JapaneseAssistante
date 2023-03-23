import pyaudio

p = pyaudio.PyAudio()

print("Liste des sorties audio activées :")
for i in range(p.get_device_count()):
    device = p.get_device_info_by_index(i)
    if device["maxOutputChannels"] > 0 and device["hostApi"] == p.get_default_host_api_info()["index"]:
        print(f"{i}: {device['name']}")
