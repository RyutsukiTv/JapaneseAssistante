import asyncio
import json
import discord
from datetime import datetime
FILE_PATH = 'codeGpt.txt'
with open('data.json', 'r') as f:
    data = json.load(f)

TOKEN = data['DISCORDBOT'] # Remplacez cela par votre propre jeton Discord
CHANNEL_ID = 1084919253242749192 # Remplacez cela par l'ID du canal Discord que vous souhaitez utiliser

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Bot connecté en tant que {0.user}'.format(client))
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%d/%m/%Y")+' '
    # Ouverture et lecture du fichier texte
    with open("./discordbot/codeContent.txt", "r") as f:
        contenu = f.read()
    quote_text = current_date+current_time+'**=======================================================**\n'+contenu+'\n **=======================================================**'
    # Envoi du contenu du fichier sur le canal général
    general_channel = client.get_channel(CHANNEL_ID)
    await general_channel.send(quote_text)

client.run(TOKEN)

           # casse les couilles fait le en java pour envoyer le txt