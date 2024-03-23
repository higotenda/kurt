"""
A module to connect to redis.
"""

import abcs

class RedisProvider(abcs.DataProvider):
	def __init__(self, host):
		self.r = redis.Redis(host=host, decode_responses=True);

	def write(self, media_str, data):
        return self.r.set(media_str, data);

    def fetch(self, media_id:str):
        return self.r.get(media_id);

    def terminate(self):
        self.r.close()