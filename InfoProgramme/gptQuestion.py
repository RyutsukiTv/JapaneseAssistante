import os
import openai
import wandb



openai.api_key = "GPTKEY"
model= 'gpt-3.5-turbo'

def model1(query):
    response = openai.Completion.create(
       prompt=query,
        model=model,
        max_tokens=500,
        n=1,
        stop=['---']
    )
    print(response)
    for result in response.choices:
        return str(result.text), str(response.usage.total_tokens)



def model2(query):
    messages = [{"role": "system", "content": ""}]
    messages.append({"role":"user","content":query})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages,max_tokens=500)
    total_tokens = response['usage']['total_tokens']
    content = response['choices'][0]['message']['content']
    return str(content), str(total_tokens)

query = "peux tu ouvrir chrome."

import string


def dernier_mot(chaine):
    # Supprimer la ponctuation de la chaîne
    chaine_propre = chaine.translate(str.maketrans('', '', string.punctuation))

    # Séparer les mots de la chaîne en une liste
    liste_mots = chaine_propre.split()

    # Récupérer le dernier mot de la liste
    dernier_mot = liste_mots[-1]

    return dernier_mot
result, token = model2(query)
if "je ne peux pas" in  result:
    nameTask = dernier_mot(query)
    result = "ouvertutr de " + nameTask

print("Cout:"+token+ "Réponse: " +result)