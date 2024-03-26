"""
A module to load config.json.
"""

from textprot import FileStorage, DummyActor, DummyProc
from procs.mux_proc import LProcMux
from provs.mongoc import MongoProvider
from impl.gemini_actor import GeminiActor
from provs.redisc import RedisProvider
import json

LLM_ACTOR_MAP = {"GeminiActor": GeminiActor, "DummyActor": DummyActor}

PROVIDER_MAP = {
    "MongoDB": MongoProvider,
    "FileStorage": FileStorage,
    "Redis": RedisProvider,
}

PROCESSOR_MAP = {"DummyProc": DummyProc, "ProcMux": LProcMux}

class Preferences:
    def __init__(self, prov, llmac, proc, token, history_limit=100):
        self.history_limit = history_limit;
        self.Provider = prov;
        self.LLM_Actor = llmac;
        self.Provider = prov;
        self.Processor = proc;
        self.TOKEN = token;

def prefs_from_provider(provider):
    serjson = provider.fetch("#prefs");
    data = json.loads(serjson)
    history_limit = data["history_limit"]
    Provider = provider;
    LLM_Actor = LLM_ACTOR_MAP[data["LLM_Actor"]](data["API_KEY"])
    Processor = PROCESSOR_MAP[data["Processor"]](data["API_KEY"])
    TOKEN = data["token"]
    return Preferences(Provider, LLM_Actor, Processor, TOKEN, history_limit);