import abcs
import redis

class RedisProvider(abcs.DataProvider):
	def __init__(self, host):
		host, _, port = host.partition(':');
		port = int(port);
		self.r = redis.Redis(host=host, port=port, decode_responses=True);

	def write(self, media_id, data):
		print("Writing to db " + media_id);
		return bool(self.r.set(media_id, data));

	def fetch(self, media_id: str):
		return abcs.Serialized(str(self.r.get(media_id)));

	def terminate(self):
		self.r.close()
