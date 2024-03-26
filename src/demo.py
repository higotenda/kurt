import impl.discordbot as bot
from impl.gemini_actor import GeminiActor
from prefs import Preferences, prefs_from_provider
from procs.mux_proc import LProcMux
from provs.redisc import RedisProvider
import sys
import os

from textprot import FileStorage

if __name__ == "__main__":
	if len(sys.argv) == 2:
		rp = RedisProvider(sys.argv[1]);
		p = prefs_from_provider(rp);
	else:
		print("Warning: Mongo is dead and we have killed him.");
		api_key = os.environ['GOOGLE_APIKEY'];
		bot_token=os.environ['DISCORD_BOT_TOKEN'];
		p = Preferences(FileStorage('./dump.bin'), GeminiActor(api_key), LProcMux(api_key), bot_token);
	bot.run(p);
