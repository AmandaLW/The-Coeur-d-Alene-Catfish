from pymongo import MongoClient
import datetime


class MongoLogger:
    def __init__(self):
        client = MongoClient('localhost:27017')
        self.db = client.g2x

    def log(self, device, property, value):
        now = datetime.datetime.utcnow()
        self.db.readings.insert({
            "timestamp": now,
            "device": device,
            "property": property,
            "value": value
        })
