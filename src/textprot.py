"""
A module to implement a CLI session to prototype..
"""

import abcs
import pickle

class ConsoleEnv(abcs.TextEnv):
	def __init__(self, prompt='>', maxlen=100):
		self.prompt = prompt;
		self.inplist = [];
		self.maxlen = maxlen;

	def loop(self, prov, proc, llmac):
		while True:
			line = input(self.prompt);
			if line == "quit":
				break;
			elif line == "kurt":
				print(abcs.kurt_init(self, prov, proc, llmac));
			else:
				self.inplist.append(line);
				if len(self.inplist) > self.maxlen:
					self.inplist.pop(0);

	def hist(self):
		links = [];
		for line in self.inplist:
			links.extend(abcs.regex_url(line));
		return (self.inplist, links);

class FileStorage(abcs.DataProvider):
	def __init__(self, fpath):
		self.fh = open(fpath, 'rb+');
		try:								# Don't want to deal with pickle shenaningans.
			self.dict = pickle.load(self.fh);
		except:								# Commit grave sin.
			self.dict = {};
			pass

	def write(self, media_str, data):
		self.dict[media_str] = data;
		return True;

	def fetch(self, media_id: str):
		return self.dict.get(media_id);

	def terminate(self):
		pickle.dump(self.dict, self.fh);
		self.fh.close();

class DummyProc(abcs.MultimediaProc):
	def __init__(self):
		pass

	def consume(self, url):
		return url;

class DummyActor(abcs.LLMActor):
	def __init__(self):
		return;

	def send_base(self, text_data, ser_data):
		return f"I'm not programmed to respond in that area. debug: {text_data}, {ser_data}"

	def send_prompt(self, text):
		return f"I'm not programmed to respond in that area. debug: {text}"


if __name__ == "__main__":
	cenv = ConsoleEnv();
	prov = FileStorage('./dump.bin');
	proc = DummyProc();
	dact = DummyActor();
	cenv.loop(prov, proc, dact);
