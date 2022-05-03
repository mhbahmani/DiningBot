from pymongo import MongoClient


class DB:

    def __init__(self, host: str = "127.0.0.1", port: int = 27017) -> None:
        self.db = MongoClient(host, int(port)).diningbotdb

    def add_user(self, user):
        self.db.users.insert_one(user)

    def add_food(self, food):
        self.db.foods.insert_one(food)

    def get_all_foods(self):
        return self.db.foods.find(
            projection={'_id': 0, 'title': 1}
            ).sort([('title', 1)])