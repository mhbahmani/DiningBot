from http import HTTPStatus
import requests
import datetime

from src.error_handlers import ErrorHandler


class Samad:
    DEFAULT_DOMAIN_SCHEME = "https://"
    SETAD_DOMAIN = DEFAULT_DOMAIN_SCHEME + "setad.dining.sharif.edu/"
    SETAD_BASE_URL = SETAD_DOMAIN + "rest/"
    RESERVES_LIST_URL = SETAD_BASE_URL + "reserves/"
    FORGET_CODE_API = SETAD_BASE_URL + "forget-card-codes/print/"

    def __init__(self, student_id: str, password: str) -> None:
        self.student_id = student_id
        self.password = password

        self.meals = []
        self.meals_id_to_name = {
            "5": "dinner",
            "1": "lunch"
        }
        self.user_id = None
        self.csrf = None
        self.remain_credit = 0
        if not self.__samad_login():
            raise (Exception(ErrorHandler.INVALID_DINING_CREDENTIALS_ERROR))
        self.headers = {
        }

    def get_current_today_all_forget_codes(self) -> list:
        today_foods = self.find_current_day_reserves()
        foods = []
        for food in today_foods:
            food_with_forget_code_and_name = self.get_forget_code(food.get("id"))
            food.update(food_with_forget_code_and_name)
            foods.append(food)
        return foods

    def find_current_day_reserves(self) -> list:
        """
        Output:
        [
            {
                meal_type_id: <str>,
                id: <str>
            }
        ]
        """
        week_reserves = self.get_current_week_reserves()
        # Date Format Example: 2023-12-25
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_reserves = []
        for reserve in week_reserves:
            if reserve.get("date") == today:
                for meal in reserve.get("mealTypes"):
                    today_reserves.append({
                        "meal_type_id": meal.get("mealTypeId"),
                        "id": meal.get("reserve").get("id")
                    })
        
        return today_reserves

    def get_current_week_reserves(self) -> list:
        params = {
            'weekStartDate': '',
        }

        response = requests.get(Samad.RESERVES_LIST_URL, params=params, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            pass
        return response.json().get("payload", {}).get("weekDays", [])

    def get_forget_code(self, reserve_id: str) -> dict:
        """
        Output:
        {
            food_name: <str>,
            forget_code: <str>
        }
        """
        params = {
            'reserveId': f'{reserve_id}',
            'count': '1',
            'dailySale': 'false',
        }

        response = requests.get(Samad.FORGET_CODE_API, params=params, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            pass
        return {
            "food_name": response.json().get("payload", {}).get("foodName"),
            "forget_code": response.json().get("payload", {}).get("forgotCardCode")
        }

    def __samad_login(self) -> bool:
        # TODO
        return True

    def check_username_and_password(username: str, password: str) -> bool:
        # TODO
        pass