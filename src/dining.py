import logging
from bs4 import BeautifulSoup as bs
import requests
import re


class Dining:
    FOODS_FILE_PATH = "./foods.txt"

    SSO_BASE_URL = "https://sso.stu.sharif.ir"
    DINING_BASE_URL = "https://dining.sharif.ir/admin"
    SIGN_IN_URL = SSO_BASE_URL + "/students/sign_in"
    RESERVE_FOOD_URL = DINING_BASE_URL + "/food/food-reserve/do-reserve-from-diet"
    RESERVE_PAGE_URL = DINING_BASE_URL + "/food/food-reserve/reserve"
    CANCEL_FOOD_URL = DINING_BASE_URL + "/food/food-reserve/cancel-reserve"
    LOAD_FOOD_TABLE = DINING_BASE_URL + "/food/food-reserve/load-reserve-table"

    FOOD_ID_REGEX = "do_reserve_from_diet\(\"(?P<food_id>\w+).*"
    DATE_REGEX = "\W+(?P<day>\w+\W?\w+)\W+(?P<date>\d+/\d+/\d+).*"

    FOOD_TIMES = ["eftari", "sahari", "dinner", "lunch"]

    def __init__(self, student_id: str, password: str) -> None:
        self.student_id = student_id
        self.password = password

        
    def reserve_food(self, user_id: int, place_id: int, food_id: int):
        params = {'user_id': user_id,}
        data = {
            'id': food_id,
            'place_id': place_id,
        }

        res = self.session.get(Dining.RESERVE_FOOD_URL, params=params, data=data)
        print(res.json())

    def test(self):
        self.__login()
        self.__load_food_table()

    def cancel_food(self, user_id: int, food_id: int):
        params = {'user_id': user_id,}
        data = {'id': food_id,}

        res = self.session.get(Dining.CANCEL_FOOD_URL, params=params, data=data)
        # TODO

    def __login(self) -> None:
        logging.debug("Making session")
        self.session = requests.Session()
        logging.debug("Get login page")
        site = self.session.get(Dining.SIGN_IN_URL)
        content = bs(site.content, "html.parser")
        authenticity_token = content.find("input", {"name":"authenticity_token"}).get('value')
        login_data = {
            'authenticity_token': authenticity_token,
            'student[student_identifier]': self.student_id,
            'student[password]': self.password,
            'commit': 'ورود به حساب کاربری'
        }
        response = self.session.post(Dining.SIGN_IN_URL, login_data)
        if response.status_code != 200:
            return False
        self.session.get(Dining.DINING_BASE_URL)
        
        logging.debug("Logged in as %s", self.student_id)
        logging.debug("Update session cookies and headers")
        csrf_token = bs(response.content, "html.parser").find("meta", {"name": "csrf-token"}).get('content')
        self.session.headers['X-CSRF-Token'] = csrf_token
        self.session.headers['X-Requested-With'] = "XMLHttpRequest"
        self.session.headers['Cookie'] = \
            f"PHPSESSID={list(self.session.cookies)[0].value}; _csrf={list(self.session.cookies)[1].value}"

        response = self.session.get(Dining.RESERVE_PAGE_URL)
        s = bs(response.content, "html.parser").find(
            "select", {"id": "foodreservesdefineform-self_id", "class": "form-control"}).attrs["onchange"][-10:]
        self.user_id = re.search("\w+", s).group()

    def __load_food_table(self) -> requests.Response:
        data = {
            'id': '0',
            'parent_id': '21',
            'week': '1',
            'user_id': self.user_id,
        }

        res = self.session.post(Dining.LOAD_FOOD_TABLE, data=data)
        return res

    def __parse_food_table(self, response: requests.Response):
        content = bs(response.content, "html.parser")
        foods = content.find("table").find_all("td")
        days = content.find("table").find_all("th")[5:]
        res = {}
        food_times = len(foods) // 7
        for i in range(7):
            day, date = re.match(Dining.DATE_REGEX, days.pop().text).groupdict().values()
            time = f"{date} {day}"
            res[time] = {}
            for i in range(food_times):
                food = foods.pop()
                food_name = food.find("span", {"data-original-title": "رزرو"})
                if food_name:
                    res[time][Dining.FOOD_TIMES[i]] = {
                        "food": food.getText(),
                        "food_id": re.match(Dining.FOOD_ID_REGEX, food_name.get("onclick")).group("food_id"),
                    }
        return res