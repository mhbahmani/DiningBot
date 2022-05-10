from pymongo import MongoClient


class DB:

    def __init__(self, host: str = "127.0.0.1", port: int = 27017) -> None:
        self.db = MongoClient(host, int(port)).diningbotdb

    def add_user(self, user):
        self.db.users.insert_one(user)

    def add_food(self, food):
        self.db.foods.insert_one(food)

    def add_forget_code(self, forget_code: dict):
        self.db.forget_codes.insert_one(forget_code)

    def update_user_forget_code_counts(self, username: str, user_id: str, count: int):
        self.db.user_forget_code_counts.update(
            {'user_id': user_id},
            {'$set': {'count': count, 'username': username}}, upsert=True
        )

    def get_all_foods(self, name: bool = False, id: bool = False):
        return self.db.foods.find(
            projection={'_id': False, 'name': name, 'id': id}
            ).sort([('food_id', 1)])

    def set_user_food_priorities(self, user_id: str, priorities: list):
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'priorities': priorities}}
        )

    def find_forget_code(self, food_court_id: int = None):
        return self.db.forget_codes.find(
            filter={"food_court_id": food_court_id},
            projection={'_id': 0, "forget_code": 1, "username": 1, "user_id": 1})

    def clear_forget_codes(self):
        self.db.forget_codes.delete_many({})