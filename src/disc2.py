import discord
import abcs
import prefs
import concurrent.futures

loop = concurrent.futures.ThreadPoolExecutor()

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

def summarize(channel, prefs=prefs.GLOBAL_PREFS):
    pass

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    # if message.content.startswith("!create_thread"):
    #     thread_name = message.content.split(" ", 1)[1]
    #     guild = message.guild
    #     existing_channel = discord.utils.get(guild.text_channels, name=thread_name)
    #     if existing_channel:
    #         await message.channel.send(
    #             f"A channel with the name '{thread_name}' already exists!"
    #         )
    #         return

    #     category = discord.utils.get(guild.categories, name="Threads")
    #     if not category:
    #         category = await guild.create_category("Threads")

    #     new_channel = await category.create_text_channel(name=thread_name)
    #     await message.channel.send(
    #         f"Thread '{thread_name}' created in category 'Threads'!"
    #     )
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    if message.content.startswith("$summarize") or message.content.startswith("$s"):
        await message.channel.send("Got prompt!")
        message.channel.send("Reading messages")
        messages = [
            m
            async for m in message.channel.history(
                limit=prefs.GLOBAL_PREFS.history_limit
            )
        ]
        messages = list(filter(lambda x: x.author != client.user, messages))
        messages = list(map(lambda x: f"{x.author.name} : {x.content}", messages))[::-1]
        ctx = Context(messages)
        await message.channel.send("Read messages")
        response = abcs.kurt_eat(
            ctx,
            prefs.GLOBAL_PREFS.Provider,
            prefs.GLOBAL_PREFS.Processor,
            prefs.GLOBAL_PREFS.LLM_Actor,
        )
        if len(response) > 2000:
            n = len(response) // 2000
            for i in range(n + 1):
                await message.channel.send(response[i * 2000 : (i + 1) * 2000])
        else:
            await message.channel.send(response)

    if message.content.startswith("$q"):
        await message.channel.send("Thinking")
        _, q, v = message.content.split("<|>")
        response = abcs.kurt_interrogate(q, prefs.GLOBAL_PREFS.LLM_Actor)
        await message.channel.send(response)

    if message.content.startswith("$interrogate "):
        if len(message.content) < len("$interrogate ") + 3:
            await message.channel.send("Question is too short!")
        await message.channel.send("Interrogating")
        response = abcs.kurt_interrogate(
            message.content[len("$interrogate ") :], prefs.GLOBAL_PREFS.LLM_Actor
        )
        if len(response) > 2000:
            n = len(response) // 2000
            for i in range(n + 1):
                await message.channel.send(response[i * 2000 : (i + 1) * 2000])
        else:
            await message.channel.send(response)


client.run(prefs.GLOBAL_PREFS.TOKEN)
