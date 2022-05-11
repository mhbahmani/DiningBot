from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


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
            filter={"food_court_id": food_court_id, "assigned": False},
            projection={'_id': 0, "forget_code": 1, "username": 1, "user_id": 1, "food_name": 1})

    def get_all_forget_codes(self):
        return self.db.forget_codes.find(
            projection={'_id': 0, "forget_code": 1, "username": 1, "user_id": 1, "food_name": 1})

    def clear_forget_codes(self):
        self.db.forget_codes.delete_many({})

    def get_users_forget_code_counts(self):
        return self.db.user_forget_code_counts.find(
            {},
            projection={'_id': 0, 'username': 1, 'count': 1, 'user_id': 1}
        ).sort([('count', -1)])
    
    def get_user_forget_code_counts(self, user_id: str):
        return self.db.user_forget_code_counts.find_one(
            filter={'user_id': user_id},
            projection={'_id': 0, 'count': 1}
        )

    def update_forget_code_assignment_status(self, forget_code: str, assigened: bool):
        self.db.forget_codes.update_one(
            {'forget_code': forget_code},
            {'$set': {'assigned': assigened}}
        )
    
    def increase_users(self):
        self.db.users_count.update({}, {"$inc": {"num_users": 1}}, upsert=True)

    def get_num_users(self) -> int:
        return self.db.bot_users.find().count()

    def unset_users_forget_codes(self):
        return self.db.bot_users.update_many(
            {},
            {"$set": {"forget_code": None}}
        )

    def update_user_rank(self, user_id: str, rank: int):
        self.db.user_forget_code_counts.update_one(
            {'user_id': user_id},
            {'$set': {'rank': rank}}
        )

    def get_user_rank(self, user_id: str):
        out = self.db.user_forget_code_counts.find_one(
            filter={'user_id': user_id},
            projection={'_id': 0, 'rank': 1}
        )
        if not out:
            out = {}
        return out

    def add_bot_user(self, user: dict) -> bool:
        try:
            self.db.bot_users.insert_one(user)
            return True
        except DuplicateKeyError:
            return False

    def get_forget_code_info(self, forget_code: str) -> dict:
        out = self.db.forget_codes.find_one(
            filter={'forget_code': forget_code},
            projection={'_id': 0, 'username': 1, 'user_id': 1}
        )
        if not out:
            out = {}
        return out

    def set_forget_code_for_user(self, user_id: str, forget_code: str):
        self.db.bot_users.update_one(
            {"user_id": user_id},
            {"$set": {"forget_code": forget_code}}
        )

    def get_user_current_forget_code(self, user_id: str) -> str:
        out = self.db.bot_users.find_one(
            filter={'user_id': user_id},
            projection={'_id': 0, 'forget_code': 1}
        )
        if not out:
            out = {}
        return out.get('forget_code', None)