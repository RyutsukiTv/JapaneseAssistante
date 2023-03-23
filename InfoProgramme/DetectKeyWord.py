import speech_recognition as sr

def transcribe_google_command(device_id):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_id) as source:
        print("Debut de la reconnaissance de mot clef...")
        audio = r.listen(source, phrase_time_limit=1)

    try:
        # Utilise la reconnaissance vocale de Google pour transcrire la parole
        # (d'autres moteurs de reconnaissance sont également disponibles)
        transcription = r.recognize_google(audio, language="fr-FR")
        print(f"Transcription : {transcription}")

        # Vérifie si "google" est dans la transcription (en ignorant la casse)
        if "assistante" in transcription.lower():
            print("Début de la transcription...")

            # Transcrit la parole pendant 5 secondes maximum
            with sr.Microphone(device_index=device_id) as source:
                audio = r.listen(source, phrase_time_limit=5)
            transcription = r.recognize_google(audio, language="fr-FR")
            print(f"Transcription : {transcription}")

    except sr.UnknownValueError:
        print("Impossible de reconnaître la parole.")
    except sr.RequestError as e:
        print(f"Erreur lors de la demande au service de reconnaissance vocale : {e}")


while True:
    transcribe_google_command(3)
