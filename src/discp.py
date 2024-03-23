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

DISCORD_BOT_TOKEN = None;
SETTINGS = None;
with open('./config.json', 'r') as fh:
	SETTINGS = json.load(fh);
DISCORD_BOT_TOKEN = SETTINGS['token'];

class DiscordBot:
    def __init__(self, prov, proc, llmac):
        self.prov = prov;
        self.proc = proc;
        self.llmac= llmac;

    async def on_ready(self):
      print("I have logged in as {0.user}".format(client))

    async def on_message(self, message):
        if message.author == client.user:
            return

        msg = message.content;
        channel = message.channel;

        print("msg: ", msg, "channel: ", channel);

        is_dm = isinstance(channel, discord.channel.DMChannel);
        
        tok = msg.split(' ');
        tok = tok if is_dm else tok[1:];
        
        tok.append('');

        if tok[0] == '/summarize':
            await channel.send("Summarizing current: " + channel.name);
            eater = ThreadedEater(channel, (self.prov, self.proc, self.llmac));
            eater.start();


class ThreadedEater(abcs.TextEnv, Thread):
    def __init__(self, channel, fwd_tup):
        Thread.__init__(self);
        self.channel = channel;
        self.fwd_tup = fwd_tup;
        self.text = [];

    def hist(self):
        text_lines = async_to_sync(self.channel.history(limit=SETTINGS['history_limit']));
        print(text_lines);
        for line in text_lines:
            links.extend(abcs.regex_url(line));
        return (text_lines, links);

    def run(self):
        abcs.kurt_eat(self, *self.fwd_tup);
  	
def async_to_sync(gen):
    while True:
        try:
            yield asyncio.run(gen.__anext__())
        except StopAsyncIteration:
            break 

def start_client(prov, proc, llmac):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content= True
    client = discord.Client(intents=intents)
    bot = DiscordBot(prov, proc, llmac);
    client.event(bot.on_ready);
    client.event(bot.on_message);
    return (bot, client);

if __name__ == "__main__":
    bot, client = start_client(textprot.FileStorage('./dump.bin'), textprot.DummyProc(), textprot.DummyActor());
    client.run(DISCORD_BOT_TOKEN);