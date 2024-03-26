from pymongo import MongoClient
import abcs


class MongoProvider(abcs.DataProvider):
    def __init__(self, url):
        self.client = MongoClient(url)
        self.mydb = self.client["Acedia"]
        self.mycollection = self.mydb["Kurt"]
        print("Connected to Mongo")

    def write(self, media_str, data):
        data = {"data": media_str}
        self.mydb.mycollection.insert_one(data)
        return True

    def fetch(self, media_id: str):
        return self.mydb.mycollection.find_one(media_id)

    def terminate(self):
        self.client.close()
