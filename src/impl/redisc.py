import abcs
import redis

class RedisProvider(abcs.DataProvider):
	def __init__(self, host):
		host, _, port = host.partition(':');
		port = int(port);
		self.r = redis.Redis(host=host, port=port, decode_responses=True);

	def write(self, media_str, data):
		print("Writing to db " + media_str);
		return self.r.set(media_str, data);

	def fetch(self, media_id: str):
		return self.r.get(media_id);

	def terminate(self):
		self.r.close()
