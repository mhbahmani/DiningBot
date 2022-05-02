from pymongo import MongoClient


class DB:

    def __init__(self, host: str = "127.0.0.1", port: str = "27017") -> None:
        self.db = MongoClient(host, port).diningbot

    def add_user(self, user):
        self.db.users.insert_one(user)