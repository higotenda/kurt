import logging
import discord
import abcs
from impl.tenvs import LinesEnv
import concurrent.futures

from prefs import Preferences

loop = concurrent.futures.ThreadPoolExecutor()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

logger = logging.getLogger(__name__);
logger.setLevel('DEBUG');
DISCORD_RESPONSE_LIMIT = 2000;

GLOBAL_PREFS = None;

def stripid_msg(msg, is_dm, split=False):
    """
    Remove user id information from textual content.
    """
    first, _, last = msg.partition(" ")
    if not is_dm:
        first, _, last = last.partition(" ")
    return (first, last) if split else last

async def send_response(channel, response):
    for idx in range(0, len(response), DISCORD_RESPONSE_LIMIT):
        await channel.send(response[idx: idx + DISCORD_RESPONSE_LIMIT]);

async def make_tenv(tenv, channel, user, botname, is_dm):
    async for message in channel.history(limit=GLOBAL_PREFS.history_limit):
        if message.author == client.user:
            continue

        content = stripid_msg(message.content, is_dm).strip() # type: ignore
        
        if content == "":
            continue # Filter out blanks.
        elif botname in content:
            continue # Filter out messages mentioning the bot.

        tenv.pushline(message.author.name + " : " + content);

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    # Assume user login was successful.
    botname = "@" + client.user.name; # type: ignore
    channel = message.channel

    # Ignore self messages.
    if message.author == client.user:
        return

    is_dm: bool = isinstance(message.channel, discord.channel.DMChannel)

    # TODO: Ignore messages where the bot is not explicitly mentioned.

    command, trail = stripid_msg(message.content, is_dm, split=True)

    if command == '/summary' or command == '/s':
        tenv = LinesEnv(reverse=True);

        if len(trail) == 0:
            await channel.send("Summarizing channel: " + ("DM" if is_dm else channel.name));
            await make_tenv(tenv, channel, client.user, botname, is_dm);
            await channel.send(f"Read last {GLOBAL_PREFS.history_limit} messages. Thinking..");
        else:
            await channel.send("Summarizing trail: " + trail);
            tenv.pushline(trail);

        response = abcs.kurt_eat(
                    tenv,
                    GLOBAL_PREFS.Provider,
                    GLOBAL_PREFS.Processor,
                    GLOBAL_PREFS.LLM_Actor,
                )

    elif command == '/interrogate' or command == '/q':
        await channel.send(f"Q: {trail} Thinking..");
        response = abcs.kurt_interrogate(trail, GLOBAL_PREFS.LLM_Actor);
    else:
        response = "I am not programmed to respond in that area.";

    await send_response(channel, response);


def run(prefs: Preferences):
    global GLOBAL_PREFS;
    GLOBAL_PREFS = prefs;
    client.run(prefs.TOKEN);