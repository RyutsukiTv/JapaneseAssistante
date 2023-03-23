import asyncio
import pyaudio
import wave
import keyboard
import speech_recognition as sr
import json
from threading import Thread
from urllib.parse import urlencode
import requests
import sounddevice as sd
import soundfile as sf
import openai
from dotenv import load_dotenv
import subprocess
import time

load_dotenv()

with open('data.json', 'r') as f:
    data = json.load(f)

# Voice out & input parameter
MICROID = 4
OUTPUTVIRTUAL = 6
OUTPUTHEAD = 10

# DeepL parameter
AUTHKEYDEEPL = data['clefDeepL']
INPUTLANG2 = "JA"
INPUTLANG1 = "fr-FR"
TARGETLANG = "FR"
URLDEEPL = "https://api-free.deepl.com/v2/translate"

# Voicevox settings
VOICEVOXAPIURL = 'http://localhost:50021'
VOICE_ID = 10
SPEED_SCALE = 1
VOLUME_SCALE = 1
INTONATION_SCALE = 1
VOICEVOX_WAV_PATH = 'wavFile/voicevox.wav'
VOICEVOXLISTEN_WAV_PATH ='wavFile/isListen.wav'
VOICEVOXDISCORD_WAV_PATH = 'wavFile/discordResponse.wav'
# keyword starting listening
KEYWORD = "assistante"

# ChatGPT
openai.api_key = data['GPTkeyApi']
model = 'text-davinci-003'
previous = ""


def transcribe_google_command(device_id):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_id) as source:
        print("is listen")
        audio = r.listen(source)
    try:
        transcription = r.recognize_google(audio, language="fr-FR")
        if KEYWORD in transcription.lower():
            print("Début de la demande")
            #threadSpeak(VOICEVOXLISTEN_WAV_PATH)
            with sr.Microphone(device_index=device_id) as source:
                audio = r.listen(source, phrase_time_limit=20, timeout=5)
            transcription = r.recognize_google(audio, language="fr-FR")
            return transcription, True
        if "au revoir" in transcription.lower():
            print("Bye bye")
            return "endCode", True
        return "", False

    except sr.UnknownValueError:
        return "", False
    except sr.RequestError as e:
        print(f"Erreur lors de la demande au service de reconnaissance vocale : {e}")
        return "", False

def transcribeWisperIA(device_id):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_id) as source:
        print("MIC ON")
        audio = r.listen(source)
    try:
        transcription = openai.Audio.translate("whisper-1", audio)
        if KEYWORD in transcription.lower():
            print("Ask Question:")
            #threadSpeak(VOICEVOXLISTEN_WAV_PATH)
            with sr.Microphone(device_index=device_id) as source:
                audio = r.listen(source, phrase_time_limit=20, timeout=5)
            transcription = openai.Audio.translate("whisper-1", audio)
            return transcription, True
        if "au revoir" in transcription.lower():
            print("Bye bye")
            return "endCode", True
        return "", False

    except sr.UnknownValueError:
        return "", False
    except sr.RequestError as e:
        print(f"Erreur lors de la demande au service de reconnaissance vocale : {e}")
        return "", False





def translate(text):
    response = requests.post(URLDEEPL, data={
        "text": text,
        "source_lang": INPUTLANG2,
        "target_lang": TARGETLANG,
        "auth_key": AUTHKEYDEEPL
    })
    translation = response.json()["translations"][0]["text"]
    return translation


def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def play_voice(device_id,wavPath):
    data, fs = sf.read(wavPath, dtype='float32')
    sd.play(data, fs, device=device_id)
    sd.wait()


def speak_jp(sentence, txt1):
    # generate initial query
    params_encoded = urlencode({'text': sentence, 'speaker': VOICE_ID})
    r = requests.post(f'{VOICEVOXAPIURL}/audio_query?{params_encoded}')
    if r.status_code == 404:
        print('Unable to reach Voicevox, ensure that it is running, or the VOICEVOX_BASE_URL variable is set correctly')
        return

    voicevox_query = r.json()
    voicevox_query['speedScale'] = SPEED_SCALE
    voicevox_query['volumeScale'] = VOLUME_SCALE
    voicevox_query['intonationScale'] = INTONATION_SCALE

    # synthesize voice as wav file
    params_encoded = urlencode({'speaker': VOICE_ID})
    r = requests.post(f'{VOICEVOXAPIURL}/synthesis?{params_encoded}', json=voicevox_query)

    with open(VOICEVOX_WAV_PATH, 'wb') as outfile:
        outfile.write(r.content)

    write_to_file("subtitle.txt", txt1)
    print(txt1)

    # play voice to app mic input and speakers/headphones
    threads = [Thread(target=play_voice, args=[OUTPUTVIRTUAL, VOICEVOX_WAV_PATH]),
               Thread(target=play_voice, args=[OUTPUTHEAD, VOICEVOX_WAV_PATH])]
    [t.start() for t in threads]
    [t.join() for t in threads]


def threadSpeak(wavpath):
    threads = [Thread(target=play_voice, args=[OUTPUTVIRTUAL,wavpath]), Thread(target=play_voice, args=[OUTPUTHEAD,wavpath])]
    [t.start() for t in threads]
    [t.join() for t in threads]

def gptmodel1(query):
    newquery = previous + query
    print(newquery)
    response = openai.Completion.create(
        prompt=newquery,
        model=model,
        max_tokens=500,
        n=1,
        stop=['---']
    )
    for result in response.choices:
        if "```" in result.text:
            print(result.text)
            return "La reponse contient du code elle sera envoyer sur discord", str(response.usage.total_tokens)
        else:
            return str(result.text), str(response.usage.total_tokens)


def gptmodel2(query):
    newquery = previous + query
    messages = [{"role": "system", "content": ""}]
    messages.append({"role": "user", "content": newquery})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=500)
    total_tokens = response['usage']['total_tokens']
    content = response['choices'][0]['message']['content']

    if "```" in content:
        write_to_file("discordbot/codeContent.txt", str(content))
        discordBotWriteOnChat()
        return "discord", str(total_tokens)
    if len(str(content))>300:
        print(len(str(content)))
        write_to_file("discordbot/codeContent.txt", translate(str(content)))
        discordBotWriteOnChat()
        return "discord", str(total_tokens)
    return str(content), str(total_tokens)


def discordBotWriteOnChat():
    p = subprocess.Popen(['python', './discordbot/bot.py'])
    time.sleep(8)
    p.terminate()

async def main():
    while True:
        txt1, bool = transcribe_google_command(MICROID)
        if bool:
            break

    if txt1 != "endCode":
        result, token = gptmodel2(txt1)
        print(result)
        if result !="discord":
            speak_jp(result, translate(result))
        else:
            threadSpeak(VOICEVOXDISCORD_WAV_PATH)
        return True
    else:
        threadSpeak("./wavFile/byebye.wav")
        return False


if __name__ == "__main__":
    print("Lancement du Logiciel")
    while True:
        if asyncio.run(main()):
            print("Fin retransmission")
        else:
            break
