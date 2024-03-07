from http import HTTPStatus
from bs4 import BeautifulSoup as bs
import requests
import datetime
import logging
import re

from src.error_handlers import ErrorHandler


class Samad:
    DEFAULT_DOMAIN_SCHEME = "https://"
    SETAD_DOMAIN = DEFAULT_DOMAIN_SCHEME + "setad.dining.sharif.edu/"
    SAMAD_DOMAIN = DEFAULT_DOMAIN_SCHEME + "samad.app"
    SAMAD_BASE_URL = SAMAD_DOMAIN + "/"
    SETAD_BASE_URL = SETAD_DOMAIN + "rest/"
    RESERVES_LIST_URL = SETAD_BASE_URL + "reserves/"
    FORGET_CODE_API = SETAD_BASE_URL + "forget-card-codes/print/"
    LOGIN_PAGE_URL = SAMAD_BASE_URL + "login/"
    OAUTH_TOKEN_URL = SETAD_DOMAIN + "oauth/token"
    RESERVE_TABLE_URL = SETAD_BASE_URL + "programs/v2/"
# https://setad.dining.sharif.edu/oauth/token

    def __init__(self, student_id: str, password: str) -> None:
        self.student_id = student_id
        self.password = password

        self.meals = []
        self.meals_id_to_name = {
            "5": "dinner",
            "1": "lunch",
            "2": "sahari",
            "4": "eftari"
        }
        self.user_id = None
        self.csrf = None
        self.remain_credit = 0

        if not self.__samad_login():
            raise (Exception(ErrorHandler.INVALID_DINING_CREDENTIALS_ERROR))
        self.headers = {}

    def get_current_day_all_forget_codes(self) -> list:
        """
        Output:
        [
            {
                meal_type_id: <str>,
                id: <str>,
                food_name: <str>,
                forget_code: <str>,
                food_court_name: <src>
            }
        ]
        """
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
                id: <str>,
                food_court_name: <src>
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
                        "id": meal.get("reserve", {}).get("id"),
                        "food_court_name": meal.get("reserve").get("selfName")
                    })
        
        return today_reserves

    def get_current_week_reserves(self) -> list:
        params = {
            'weekStartDate': '',
        }

        response = self.session.get(Samad.RESERVES_LIST_URL, params=params, headers=self.headers)
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

        response = self.session.get(Samad.FORGET_CODE_API, params=params, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            pass
        return {
            "food_name": response.json().get("payload", {}).get("foodName").replace("|", ""),
            "forget_code": response.json().get("payload", {}).get("forgotCardCode")
        }

    def __samad_login(self) -> bool:
        try:
            self.session = requests.Session()
            login_page = self.session.get(Samad.LOGIN_PAGE_URL)
            # extract main java script url from this html with bs
            soup = bs(login_page.content, 'html.parser')
            for js_url in soup.find_all('script'):
                if js_url.get('src') and "main" in js_url.get('src'):
                    main_js_uri = js_url.get('src')
                    break
            # get main js file
            main_js = self.session.get(Samad.SAMAD_DOMAIN + main_js_uri)

            for authorization_elemnt in main_js.text.split("Authorization:"):
                if "Basic" in authorization_elemnt and re.search(r'Basic \w+=*\"\,\"Content-Type\":\"application/x-www-form-urlencoded', authorization_elemnt):
                    authorization_header = authorization_elemnt.split("}")[0].strip().replace('"', '').split(",")[0]
                    break

            headers = {"authorization": authorization_header}

            data = {
                'username': self.student_id,
                'password': self.password,
                'grant_type': 'password',
                'scope': 'read+write',
            }

            # perform main login request
            response = self.session.post(Samad.OAUTH_TOKEN_URL, headers=headers, data=data)
            if response.status_code != HTTPStatus.OK:
                return False

            # get user authorization and refresh token
            authorization_token = response.json().get("access_token")
            # Add authorization token to session headers
            self.session.headers.update({"Authorization": f"Bearer {authorization_token}"})
            self.refresh_token = response.json().get("refresh_token")
            return True
        except Exception as e:
            logging.error(f"Login to samad failed: {e}")
            return False

    def check_user_week_reservation_status(self, food_court_id):
        # Get date of the start of the next week starting date in 2024-01-06 00:00:00 format
        now = datetime.datetime.now()
        next_week_start_date = (now + datetime.timedelta(days=(7 - now.weekday() - 2))).strftime("%Y-%m-%d 00:00:00")

        params = {
            'selfId': str(food_court_id),
            'weekStartDate': next_week_start_date,
        }
        response = self.session.get(
            Samad.RESERVE_TABLE_URL,
            headers=self.headers,
            params=params
        )

        if response.status_code != HTTPStatus.OK:
            pass

        if response.json().get("payload", {}).get("userWeekReserves"):
            return True
        return False

    def check_username_and_password(username: str, password: str) -> bool:
        # TODO
        pass