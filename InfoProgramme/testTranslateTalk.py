import asyncio
import audioop
import pyaudio
import wave
import speech_recognition as sr
import json
from threading import Thread
from urllib.parse import urlencode
import requests
import sounddevice as sd
import soundfile as sf

from dotenv import load_dotenv

with open('../data.json', 'r') as f:
    data = json.load(f)

# Voice out Input parameter
voice_chan = 3
voice_virtual = 8
voice_headphone = 6

enterLanguage = "fr-FR"
voiceCharact = 1

# DeepL parameter
auth_key = data['clefDeepL']
text = "Hello, comment ça va ?"
source_lang = "FR"
target_lang = "JA"
url = "https://api-free.deepl.com/v2/translate"

load_dotenv()

# Audio devices
SPEAKERS_INPUT_ID = 8
APP_INPUT_ID = 6

# Voicevox settings
BASE_URL = 'http://localhost:50021'
VOICE_ID = 20
SPEED_SCALE = 0.94
VOLUME_SCALE = 1
INTONATION_SCALE = 1

VOICEVOX_WAV_PATH = '../wavFile/voicevox.wav'




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


def translate(text):
    print("traduction en cours")
    response = requests.post(url, data={
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "auth_key": auth_key
    })
    translation = response.json()["translations"][0]["text"]
    return translation


def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def play_voice(device_id):
    data, fs = sf.read(VOICEVOX_WAV_PATH, dtype='float32')
    sd.play(data, fs, device=device_id)
    sd.wait()


def speak_jp(sentence, txt1):
    print("speaker en cours")
    # generate initial query
    params_encoded = urlencode({'text': sentence, 'speaker': VOICE_ID})
    r = requests.post(f'{BASE_URL}/audio_query?{params_encoded}')
    if r.status_code == 404:
        print('Unable to reach Voicevox, ensure that it is running, or the VOICEVOX_BASE_URL variable is set correctly')
        return

    voicevox_query = r.json()
    voicevox_query['speedScale'] = SPEED_SCALE
    voicevox_query['volumeScale'] = VOLUME_SCALE
    voicevox_query['intonationScale'] = INTONATION_SCALE

    # synthesize voice as wav file
    params_encoded = urlencode({'speaker': VOICE_ID})
    r = requests.post(f'{BASE_URL}/synthesis?{params_encoded}', json=voicevox_query)

    with open(VOICEVOX_WAV_PATH, 'wb') as outfile:
        outfile.write(r.content)

    write_to_file("../subtitle.txt", txt1)

    # play voice to app mic input and speakers/headphones
    threads = [Thread(target=play_voice, args=[APP_INPUT_ID]), Thread(target=play_voice, args=[SPEAKERS_INPUT_ID])]
    [t.start() for t in threads]
    [t.join() for t in threads]


async def main():
    txt1 ="L'univers quantique est un monde étrange où les particules subatomiques se comportent de manière bizarre et imprévisible. Les lois de la physique classique ne s'appliquent plus et la réalité n'est plus déterministe, mais probabiliste. Les particules peuvent être à deux endroits différents en même temps, et leur état peut être lié à distance sans communication apparente. L'univers quantique est également marqué par l'importance de l'observateur, car la mesure d'une particule peut influencer son état. Cet univers mystérieux est le terrain de jeu de la physique quantique, qui cherche à comprendre et à exploiter ces phénomènes pour des applications technologiques."

    txt2 = translate(txt1)

    if txt2 != "情報処理エラー":
        print(txt2)
        speak_jp(txt2, txt1)

        print("Vous pouvez de nouveau parler")



if __name__ == "__main__":
    asyncio.run(main())