from bs4 import BeautifulSoup as bs
from http import HTTPStatus
from src.error_handlers import ErrorHandler
import src.static_data as static_data
import logging
import requests
import re


class Dining:
    SSO_BASE_URL = "https://sso.stu.sharif.ir"
    DINING_BASE_URL = "https://setad.dining.sharif.edu"
    SIGN_IN_URL = SSO_BASE_URL + "/students/sign_in"
    SHARIF_AUTHORIZATION_ADDRESS = 'https://setad.dining.sharif.edu/oauth2/authorization/sharif?' \
                                   'client_id=4097ab763c951ae4dafd7fb645cacb9462e81ba8b7d98eb3a269ebdcef33b523&' \
                                   'amp;redirect_uri=https://setad.dining.sharif.edu:443/oauth2/authorization/sharif&' \
                                   'amp;response_type=code&amp;scope=read&amp;state=IBuwSV'
    SETAD_OAUTH_REDIRECT = 'https://setad.dining.sharif.edu/index.rose?sharifOauthRedirect=true'
    RESERVE_FOOD_URL = DINING_BASE_URL + "/nurture/user/multi/reserve/reserve.rose"
    RESERVE_PAGE_URL = DINING_BASE_URL + "/nurture/user/multi/reserve/reserve.rose"
    CANCEL_FOOD_URL = DINING_BASE_URL + "/food/food-reserve/cancel-reserve"
    LOAD_FOOD_TABLE = DINING_BASE_URL + "/food/food-reserve/load-reserve-table"

    FOOD_ID_REGEX = "do_reserve_from_diet\(\"(?P<food_id>\w+).*"
    FOOD_NAME_AND_PRICE_REGEX = "(?P<name>.*)\W\((?P<price>\d+,\d+) تومان\)"
    DATE_REGEX = "\W+(?P<day>\w+\W?\w+)\W+(?P<date>\d+/\d+/\d+).*"

    def __init__(self, student_id: str, password: str) -> None:
        self.student_id = student_id
        self.password = password

        self.meals = []
        self.user_id = None
        self.csrf = None
        self.remainCredit = 0
        if not self.__login():
            raise (Exception(ErrorHandler.NOT_ALLOWED_TO_RESERVATION_PAGE_ERROR))

    def reserve_food(self, place_id: int, food_id: int) -> bool:
        logging.debug("Reserving food %s", food_id)
        params = {'user_id': self.user_id, }
        data = {
            'weekStartDateTime': '1680975736863',
            'remainCredit': '',
            'method%3AshowPanel': 'Submit',
            'selfChangeReserveId': '',
            'weekStartDateTimeAjx': '1680975736873',
            'freeRestaurant': '',
            'selectedSelfDefId': str(place_id),
        }
        for i in range(len(self.foods)):
            subData = {
                f"userWeekReserves{i}.selected": "false",
                f"userWeekReserves{i}.selectedCount": "1",
                f"userWeekReserves{i}.id": "",
                f"userWeekReserves{i}.programId": "37973",
                f"userWeekReserves{i}.mealTypeId": "1",
                f"userWeekReserves{i}.programDateTime": "1678480200000",
                f"userWeekReserves{i}.selfId": place_id,
                f"userWeekReserves{i}.foodTypeId": "644",
                f"userWeekReserves{i}.foodId": "66",
                f"userWeekReserves{i}.priorReserveDateStr": "null",
                f"userWeekReserves{i}.freeFoodSelected": "false"
            }
            response = self.session.get(Dining.RESERVE_FOOD_URL, params=params, data=data)
        if response.json().get("success"):
            return True, response.json().get("balance")
        return False, 0
        # TODO: Handle balance on failure

    def cancel_food(self, user_id: int, food_id: int):
        params = {'user_id': user_id, }
        data = {'id': food_id, }
        res = self.session.get(Dining.CANCEL_FOOD_URL, params=params, data=data)
        print(res.json())
        # TODO

    def get_foods_list(self, place_id: int, week: int = 1) -> list:
        table = self.__load_food_table(place_id=place_id, week=week)
        if table.status_code != HTTPStatus.OK:
            logging.debug("Something went wrong with status code: %s", table.status_code)
            return []
        return self.__parse_food_table_to_get_foods_list(table)

    def get_reserve_table_foods(self, place_id: int, week: int = 1) -> dict:
        """ output:
        {
            <date>: {
                <food_time>: {
                    food: <food_name>,
                    price: <price>,
                    food_id: <food_reserve_id>
                }
            }
        """
        table = self.__load_food_table(place_id=place_id, week=week)
        self.remainCredit = bs(table.content, "html.parser").find("span", {"id": "creditId"})
        if table.status_code != HTTPStatus.OK:
            logging.debug("Something went wrong with status code: %s", table.status_code)
            return {}
        return self.__parse_reserve_table(table)

    def __login(self) -> bool:
        logging.debug("Making session")
        self.session = requests.Session()
        logging.debug("Get login page")
        site = self.session.get(Dining.SIGN_IN_URL)
        content = bs(site.content, "html.parser")
        authenticity_token = content.find("input", {"name": "authenticity_token"}).get('value')
        login_data = {
            'authenticity_token': authenticity_token,
            'student[student_identifier]': self.student_id,
            'student[password]': self.password,
            'commit': 'ورود به حساب کاربری'
        }
        response = self.session.post(Dining.SIGN_IN_URL, login_data)
        if response.status_code != 200:
            return False
        self.session.get(Dining.SETAD_OAUTH_REDIRECT)
        self.session.get(Dining.SHARIF_AUTHORIZATION_ADDRESS)
        logging.debug("Logged in as %s", self.student_id)
        logging.debug("Update session cookies and headers")
        reserve_page = self.session.get(Dining.RESERVE_PAGE_URL)
        self.csrf = bs(reserve_page.content, "html.parser").find("input", {"name": "_csrf"}).get("value")
        if str(reserve_page.text).find('ورود به سامانه سماد') != -1:
            logging.debug("Login failed")
            return False
        return True

    def check_username_and_password(username: str, password: str) -> bool:
        logging.debug("Making session")
        session = requests.Session()
        logging.debug("Get login page")
        site = session.get(Dining.SIGN_IN_URL)
        content = bs(site.content, "html.parser")
        authenticity_token = content.find("input", {"name": "authenticity_token"}).get('value')
        login_data = {
            'authenticity_token': authenticity_token,
            'student[student_identifier]': username,
            'student[password]': password,
            'commit': 'ورود به حساب کاربری'
        }
        response = session.post(Dining.SIGN_IN_URL, login_data)
        if bs(response.content, "html.parser").find("div", {"class": "card-alert alert alert-warning mb-0"}):
            logging.debug("Login failed")
            return False
        logging.debug("Login successful")

        return True

    def __load_food_table(self, place_id: int, week: int = 1) -> requests.Response:
        data = {
            'weekStartDateTime': '1680975736863',
            'remainCredit': '',
            'method%3AshowPanel': 'Submit',
            'selfChangeReserveId': '',
            'weekStartDateTimeAjx': '1680975736873',
            'freeRestaurant': '',
            'selectedSelfDefId': str(place_id),
            '_csrf': self.csrf,
        }

        return self.session.post(Dining.RESERVE_FOOD_URL, data=data)

    def __parse_reserve_table(self, reserve_table: requests.Response) -> dict:
        content = bs(reserve_table.content, "html.parser").find("td", {"id": "pageTD"}).findNext("table").findNext(
            "table")
        self.meals = [static_data.MEAL_FA_TO_EN[time.text.split(("\n"))[1].strip()] for time in
                      content.findNext("tr").find_all("td")]
        self.meals.reverse()  # TOF MALI :)
        days = []
        foods = []
        content = content.find_all("tr", recursive=False)
        numberOfState = len(content[0].find_next("td").find_next_siblings("td"))
        for i in range(len(content)):
            food = content[i].find_next("td")
            for j in range(numberOfState + 1):
                if j == 0:
                    days.append(food)
                    food = food.find_next_siblings("td")
                else:
                    foods.append(food[j - 1])
        days.reverse()
        res = {}
        food_times = numberOfState
        for i in range(len(days)):
            day, date = days[i].text.split("\n")[1].strip(), days[i].find_next("div").text
            time = f"{date} {day}"
            res[time] = {}
            for j in range(food_times):
                res[time][self.meals[j]] = res[time].get(self.meals[j], [])
                food = foods.pop()
                foods_row = food.find_next("table").find_all("table")
                for food_row in foods_row:
                    food_name = food_row.find_next("span").text.split("|")[1]
                    price = food_row.find_next("div", {"class", "xstooltip"}).text.strip().split("\n")[0]
                    food_reserve_function = food_row.find_next("span")
                    food_id = food_reserve_function.get("id").split("_")[1]
                    if food_reserve_function:
                        res[time][self.meals[j]].append({
                            "food": food_name,
                            "price": price,
                            "food_id": food_id,
                        })
        self.foods = dict(reversed(list(res.items())))
        return self.foods

    def __parse_food_table_to_get_foods_list(self, table: requests.Response) -> list:
        content = bs(table.content, "html.parser")
        foods = content.find("table").find_all("td")
        result = []
        for food in foods:
            if len(food.find_all("div")) != 1:
                for day_food in food.find_all("div"):
                    food_name = re.sub(" \(.*\)", "", day_food.getText())
                    if food_name != "-":
                        result.append(food_name.strip())
                continue
            food_name = re.sub(" \(.*\)", "", food.getText())
            if food_name != "-":
                result.append(food_name.strip())
        return result

    def __parse_reserve_page_to_get_food_courts(self, reserve_page: requests.Response) -> dict:
        content = bs(reserve_page.content, "html.parser")
        return dict(map(lambda x: (x.getText(), x.attrs["value"]), content.find_all("option")))

    def get_user_food_courts(self):
        response = self.session.get(Dining.RESERVE_PAGE_URL)
        return self.__parse_reserve_page_to_get_food_courts(response)
