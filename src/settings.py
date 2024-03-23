"""
A module to load config.json.
"""

from textprot import FileStorage, DummyActor, DummyProc
from impl.mongoc import MongoProvider
from impl.actor import GeminiActor
import json

SETTINGS = None;
with open('./config.json', 'r') as fh:
	SETTINGS = json.load(fh);

LLM_ACTOR_MAP = {
	'GeminiActor': GeminiActor,
	'DummyActor': DummyActor
};

PROVIDER_MAP = {
	'MongoDB': MongoProvider,
	'FileStorage': FileStorage
};

PROCESSOR_MAP = {
	'DummyProc': DummyProc
};

SETTINGS['LLM_Actor']= LLM_ACTOR_MAP[SETTINGS['LLM_Actor']](SETTINGS['ACTARG']);
SETTINGS['Provider'] = PROVIDER_MAP[SETTINGS['Provider']](SETTINGS['PRVARG']);
SETTINGS['Processor']= PROCESSOR_MAP[SETTINGS['Processor']]();