DISCORD_KEY, GEMINI_KEY = None, None
with open("apikeys.txt") as f:
    DISCORD_KEY, GEMINI_KEY = f.readlines()

import discord
import abcs
import settings

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

class Context(abcs.TextEnv):
    def __init__(self, messages):
        self.messages = messages
    
    def hist(self):
        links = []
        for line in self.messages:
            links.extend(abcs.regex_url(line))
        return (self.messages, links)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

channels = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$summarize'):
        print("Got prompt!")
        messages = [m async for m in message.channel.history(limit=200)]
        messages = list(filter(lambda x: x.author!=client.user, messages))
        messages = list(map(lambda x: x.content, messages))
        response = abcs.kurt_eat(Context(messages), settings.PROVIDER_MAP["FileStorage"]('dump.bin'), settings.PROCESSOR_MAP["ProcMux"](), settings.LLM_ACTOR_MAP["GeminiActor"](GEMINI_KEY))
        await message.channel.send(response)
    if message.content.startswith('$interrogate '):
        if len(message.content)<len('$interrogate ')+3:
            await message.channel.send("Question is too short!")
        response = abcs.kurt_interrogate(Context(messages), settings.PROVIDER_MAP["FileStorage"]('dump.bin'), settings.PROCESSOR_MAP["ProcMux"](), settings.LLM_ACTOR_MAP["GeminiActor"](GEMINI_KEY))
        await message.channel.send(response)

client.run(DISCORD_KEY)