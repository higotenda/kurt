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

from settings import SETTINGS

DISCORD_BOT_TOKEN = SETTINGS['token'];
client = None;

class DiscordBot:
    async def on_ready(self):
      print("I have logged in as {0.user}".format(client))

    async def on_message(self, message):
        if message.author == client.user:
            return

        msg = message.content;
        channel = message.channel;
        is_dm = isinstance(channel, discord.channel.DMChannel);
        
        tok = msg.split(' ');
        tok = tok if is_dm else tok[1:];
        tok.append('');

        if tok[0] == '/summarize':
            texts = [];
            async for message in channel.history(limit=SETTINGS['history_limit']):
                content = message.content if is_dm else message.content.partition('>')[-1].strip();
                if content.strip() == '':
                    continue;   # Just filter blanks out.
                texts.append(message.author.name + " : " + content);
            await channel.send("Summarizing current: " + channel.name);
            eater = Eater(channel, texts, (SETTINGS['Provider'], SETTINGS['Processor'], SETTINGS['LLM_Actor']));
            await eater.do_it();


class Eater(abcs.TextEnv):
    def __init__(self, channel, texts, fwd_tup):
        Thread.__init__(self);
        self.channel = channel;
        self.fwd_tup = fwd_tup;
        self.texts = texts;

    def hist(self):
        links = [];
        for line in self.texts:
            links.extend(abcs.regex_url(line));
        return (self.texts, links);

    async def do_it(self):
        response = abcs.kurt_eat(self, *self.fwd_tup);
        await self.channel.send(response);

def make_client():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content= True

    global client;
    client = discord.Client(intents=intents)
    bot = DiscordBot();
    client.event(bot.on_ready);
    client.event(bot.on_message);
    return (bot, client);