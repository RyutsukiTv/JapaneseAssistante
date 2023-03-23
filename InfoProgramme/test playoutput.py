import pyaudio
import wave

def play_wav_on_outputs(wav_file, output_indices):
    CHUNK = 1024

    # Ouverture du fichier WAV
    wf = wave.open(wav_file, 'rb')

    # Initialisation de PyAudio
    p = pyaudio.PyAudio()

    # Ouverture des flux de sortie audio
    stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output_device_index=output_indices[0],
                     output=True)
    stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output_device_index=output_indices[1],
                     output=True)

    # Lecture et envoi du contenu du fichier WAV aux deux sorties audio
    data = wf.readframes(CHUNK)
    while data:
        stream1.write(data)
        stream2.write(data)
        data = wf.readframes(CHUNK)

    # Fermeture des flux de sortie audio et de PyAudio
    stream1.stop_stream()
    stream2.stop_stream()
    stream1.close()
    stream2.close()
    p.terminate()

# Exemple d'utilisation de la fonction
play_wav_on_outputs('../voice.wav', [6, 9])
