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

    if message.content.startswith('!create_thread'):
        thread_name = message.content.split(' ', 1)[1]
        guild = message.guild
        existing_channel = discord.utils.get(guild.text_channels, name=thread_name)
        if existing_channel:
            await message.channel.send(f"A channel with the name '{thread_name}' already exists!")
            return

        category = discord.utils.get(guild.categories, name='Threads')
        if not category:
            category = await guild.create_category('Threads')

        new_channel = await category.create_text_channel(name=thread_name)
        await message.channel.send(f"Thread '{thread_name}' created in category 'Threads'!")
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$summarize'):
        await message.channel.send("Got prompt!")
        
        messages = [m async for m in message.channel.history(limit=1000)]
        messages = list(filter(lambda x: x.author!=client.user, messages))
        messages = list(map(lambda x: x.content, messages))[::-1]

        await message.channel.send("Read all messages")

        ctx = Context(messages)
        response = abcs.kurt_eat(ctx, settings.SETTINGS['Provider'], settings.SETTINGS["Processor"], settings.SETTINGS['LLM_Actor'])
        if len(response)>2000:
            n = response//2000
            for i in range(n+1):
                await message.channel.send(response[i*2000:(i+1)*2000])
        else:
            await message.channel.send(response)
    if message.content.startswith('$interrogate '):
        if len(message.content)<len('$interrogate ')+3:
            await message.channel.send("Question is too short!")
        await message.channel.send("Interrogating")
        response = abcs.kurt_interrogate(message.content[len('$interrogate '):], settings.SETTINGS['LLM_Actor'])
        if len(response)>2000:
            n = response//2000
            for i in range(n+1):
                await message.channel.send(response[i*2000:(i+1)*2000])
        else:
            await message.channel.send(response)

client.run(settings.SETTINGS['token'])