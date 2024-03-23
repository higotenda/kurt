"""
A module to load config.json.
"""

from textprot import FileStorage, DummyActor, DummyProc
from impl.procs import ProcMux
from impl.mongoc import MongoProvider
from impl.actor import GeminiActor
from impl.procs import ProcMux
from impl.redisc import RedisProvider
import json

LLM_ACTOR_MAP = {
	"GeminiActor": GeminiActor,
	"DummyActor": DummyActor
};

PROVIDER_MAP = { 
	"MongoDB": MongoProvider, 
	"FileStorage": FileStorage,
	"Redis": RedisProvider
};

PROCESSOR_MAP = {
	"DummyProc": DummyProc, 
	"ProcMux": ProcMux
};

SETTINGS = None
with open("./config.json", "r") as fh:
    SETTINGS = json.load(fh)
SETTINGS["Provider"]  = PROVIDER_MAP[SETTINGS["Provider"]]  (SETTINGS["PRVARG"]);

class Preferences:
	def __init__(self, serjson):
		data = json.loads(serjson);
		self.history_limit = data['history_limit'];
		self.LLM_Actor = LLM_ACTOR_MAP[data["LLM_Actor"]](data["API_KEY"]);
		self.Processor = PROCESSOR_MAP[data['Processor']](data["API_KEY"]);
		self.TOKEN = data['token'];

GLOBAL_PREFS = Preferences(SETTINGS["Provider"].fetch("#prefs"));