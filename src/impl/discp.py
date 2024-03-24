"""
A module to implement a TextEnv that uses discord chat history.
"""

# Readers are requested to ignore various unholy sins committed hitherto.

import discord
import json
import abcs
from threading import Thread
import textprot
import asyncio

from prefs import GLOBAL_PREFS, SETTINGS

DISCORD_BOT_TOKEN = GLOBAL_PREFS.TOKEN
client = None

def stripid_msg(msg, is_dm, split=False):
    first, _, last = msg.partition(' ');
    if not is_dm:
        first, _, last = last.partition(' ');
    return (first, last) if split else last;

def stripid_msg(msg, is_dm, split=False):
    first, _, last = msg.partition(" ")
    if not is_dm:
        first, _, last = last.partition(" ")
    return (first, last) if split else last


async def on_ready():
    print("I have logged in as {0.user}".format(client))


async def on_message(message):
    if message.author == client.user:
        return

    channel = message.channel
    is_dm = isinstance(message.channel, discord.channel.DMChannel)
    command, trail = stripid_msg(message.content, is_dm, split=True)

    if command == "/summary" or command == "/.":

        texts = []

        if len(trail.strip()) == 0:
            async for message in channel.history(limit=GLOBAL_PREFS.history_limit):
                if message.author == client.user:
                    continue
                content = stripid_msg(message.content, is_dm)
                if content.strip() == "":
                    continue
                    # Just filter blanks out.
                texts.append(message.author.name + " : " + content)
            await channel.send("Summarizing current: " + channel.name)
            texts = texts[::-1]
        else:
            texts.append(trail)
            await channel.send("Summarizing trail: " + trail)
        eater = Eater(channel, texts, (SETTINGS['Provider'], GLOBAL_PREFS.Processor, GLOBAL_PREFS.LLM_Actor));
        await eater.do_it();

    elif command == '/interrogate' or command == '/?':
        response = GLOBAL_PREFS.LLM_Actor.send_prompt(trail);
        await channel.send(response[:2000]);


class Eater(abcs.TextEnv):
    def __init__(self, channel, texts, fwd_tup):
        Thread.__init__(self)
        self.channel = channel
        self.fwd_tup = fwd_tup
        self.texts = texts

    def hist(self):
        links = []
        for line in self.texts:
            links.extend(abcs.regex_url(line))
        return (self.texts, links)

    async def do_it(self):
        response = abcs.kurt_eat(self, *self.fwd_tup)
        await self.channel.send(response[:2000])


def make_client():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    global client
    client = discord.Client(intents=intents)
    client.event(on_ready)
    client.event(on_message)
    return client
