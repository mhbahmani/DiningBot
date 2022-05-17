from bs4 import BeautifulSoup as bs
import src.static_data as static_data
import http
import logging
import requests
import re


class Dining:
    SSO_BASE_URL = "https://sso.stu.sharif.ir"
    DINING_BASE_URL = "https://dining.sharif.ir/admin"
    SIGN_IN_URL = SSO_BASE_URL + "/students/sign_in"
    RESERVE_FOOD_URL = DINING_BASE_URL + "/food/food-reserve/do-reserve-from-diet"
    RESERVE_PAGE_URL = DINING_BASE_URL + "/food/food-reserve/reserve"
    CANCEL_FOOD_URL = DINING_BASE_URL + "/food/food-reserve/cancel-reserve"
    LOAD_FOOD_TABLE = DINING_BASE_URL + "/food/food-reserve/load-reserve-table"

    FOOD_ID_REGEX = "do_reserve_from_diet\(\"(?P<food_id>\w+).*"
    DATE_REGEX = "\W+(?P<day>\w+\W?\w+)\W+(?P<date>\d+/\d+/\d+).*"

    def __init__(self, student_id: str, password: str) -> None:
        self.student_id = student_id
        self.password = password
        self.__login()

    def reserve_food(self, user_id: int, place_id: int, food_id: int):
        params = {'user_id': user_id,}
        data = {
            'id': food_id,
            'place_id': place_id,
        }

        res = self.session.get(Dining.RESERVE_FOOD_URL, params=params, data=data)
        print(res.json())
        # TODO

    def cancel_food(self, user_id: int, food_id: int):
        params = {'user_id': user_id,}
        data = {'id': food_id,}

        res = self.session.get(Dining.CANCEL_FOOD_URL, params=params, data=data)
        print(res.json())
        # TODO

    def get_foods_list(self, place_id: int, week: int = 1) -> list:
        table = self.__load_food_table(place_id=place_id, week=week)
        return self.__parse_food_table_to_get_foods_list(table)

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
        res = self.session.get(Dining.DINING_BASE_URL)
        if res.status_code != http.HTTPStatus.OK:
            logging.info("Something went wrong with status code: %s", res.status_code)
            return
        logging.debug("Logged in as %s", self.student_id)
        logging.debug("Update session cookies and headers")
        csrf_token = bs(response.content, "html.parser").find("meta", {"name": "csrf-token"}).get('content')
        self.session.headers['X-CSRF-Token'] = csrf_token
        self.session.headers['X-Requested-With'] = "XMLHttpRequest"
        self.session.headers['Cookie'] = \
            f"PHPSESSID={list(self.session.cookies)[0].value}; _csrf={list(self.session.cookies)[1].value}"

        response = self.session.get(Dining.RESERVE_PAGE_URL)
        s = bs(response.content, "html.parser").find(
            "button", {"type": "button", "class": "btn btn-default navigation-link"}).get("onclick")
        self.user_id = re.match("load_diet_reserve_table.*\,(?P<user_id>\w+)\)", s).group("user_id")

    def __load_food_table(self, place_id: int, week: int = 1) -> requests.Response:
        data = {
            'id': '0',
            'parent_id': place_id,
            'week': str(week),
            'user_id': self.user_id,
        }

        res = self.session.post(Dining.LOAD_FOOD_TABLE, data=data)
        return res

    def __parse_food_table(self, reserve_table: requests.Response) -> dict:
        content = bs(reserve_table.content, "html.parser")
        food_times = [static_data.food_times_to_en[time.text] for time in content.find("table").find_all("th")[1:-7]]
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
                    res[time][food_times[i]] = {
                        "food": food.getText(),
                        "food_id": re.match(Dining.FOOD_ID_REGEX, food_name.get("onclick")).group("food_id"),
                    }
        return res

    def __parse_food_table_to_get_foods_list(self, table: requests.Response) -> list:
        content = bs(table.content, "html.parser")
        foods = content.find("table").find_all("td")
        result = []
        for food in foods:
            if len(food.find_all("div")) != 1:
                for day_food in food.find_all("div"):
                    food_name = re.sub(" \(.*\)", "" , day_food.getText())
                    if food_name != "-":
                        result.append(food_name.strip())
                continue
            food_name = re.sub(" \(.*\)", "" , food.getText())
            if food_name != "-":
                result.append(food_name.strip())
        return result