from bs4 import BeautifulSoup as bs
from http import HTTPStatus
from src.error_handlers import ErrorHandler
from src.error_handlers import (
    NotEnoughCreditToReserve,
    NoSuchFoodSchedule
)
import src.static_data as static_data
import datetime
import requests
import logging
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
    SHOW_PANEL_URL = DINING_BASE_URL + "/nurture/user/multi/reserve/showPanel.rose"
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
        if not self.__setad_login():
            raise (Exception(ErrorHandler.NOT_ALLOWED_TO_RESERVATION_PAGE_ERROR))

    def reserve_food(self, place_id: int, foods: dict, choosed_food_indices: dict) -> bool:
        """
        food: {
            food: <food_name>,
            price: <price>,
            food_id: <food_reserve_id>,
            program_id: <food_program_id>,
            program_date: <food_program_date>
        }
        """
        logging.debug("Reserving foods %s")
        # Get epoch time of 8:30:00 PM of the first day of the next week
        now = datetime.datetime.now()
        start_of_week = now - datetime.timedelta(days=(now.weekday() + 2) % 7)
        epoch_start_of_the_week = str(int(start_of_week.timestamp()) * 1000)
        epoch_start_of_the_next_week = str(int((now + datetime.timedelta(days=(7 - (now.weekday() + 2)))).replace(hour=0, minute=0, second=0).timestamp()) * 1000)

        data = [
            ('weekStartDateTime', f'{epoch_start_of_the_next_week}'),
            # ('remainCredit', '-280000'),
            ('method:doReserve', 'Submit'),
            ('_csrf', self.csrf),
            ('selfChangeReserveId', ''),
            ('weekStartDateTimeAjx', f"{epoch_start_of_the_week}"),
            ('freeRestaurant', 'false'),
            ('selectedSelfDefId', '1'),
        ]

        # i = sum([ len(foods[day]['lunch']) for day in foods ]) - 1
        i = 0
        food_data = []
        data_batch = []
        keys = list(foods.keys())
        keys.reverse()
        total_food_prices = 0
        for day in keys:
            for meal in foods[day]:
                foods_list = foods[day][meal]
                foods_list.reverse()
                for food_index, food in enumerate(foods_list):
                    food_data = []
                    if food_index == choosed_food_indices[day][meal]:
                    # if food.get("food") in ['شوید پلو با مرغ', 'چلو خورشت مسما بادمجان', 'رشته پلو با گوشت', 'چلو‌خورش بامیه', 'چلو با شامی کباب']:
                        food_data += [
                            (f"userWeekReserves[{i}].selected", 'true'),
                            (f"userWeekReserves[{i}].selectedCount", '1')
                        ]
                        total_food_prices += int(food.get("price"))

                    # Convert food['program_date'] to epoch
                    program_date_epoch = str(int(
                        datetime.datetime.strptime(food['program_date'], "%Y-%m-%d").timestamp()) * 1000)

                    food_data += [
                        (f"userWeekReserves[{i}].id", ''),
                        (f"userWeekReserves[{i}].programId", food.get("program_id")),
                        (f"userWeekReserves[{i}].mealTypeId", '1'),
                        (f"userWeekReserves[{i}].programDateTime", program_date_epoch), # Food day
                        (f"userWeekReserves[{i}].selfId", str(place_id)),
                        (f"userWeekReserves[{i}].foodTypeId", food.get("food_type_id")),
                        (f"userWeekReserves[{i}].foodId", food.get("food_id")),
                        (f"userWeekReserves[{i}].priorReserveDateStr", f'null'),
                        # (f"userWeekReserves[{i}].priorReserveDateStr", f'{food.get("program_date")} 08:00:00.0'),
                        (f"userWeekReserves[{i}].freeFoodSelected", 'false'),
                    ]
                    data_batch.append(food_data)
                    i += 1
        
        data.insert(1,('remainCredit', str(self.remainCredit - total_food_prices)))
        # data_batch.reverse()
        for d in data_batch:
            data += d

        response = self.session.post(Dining.RESERVE_FOOD_URL, data=data)
        text = bs(response.content, "html.parser").prettify()
        # with open("out.html", "w") as file:
        #     file.write(bs(response.content, "html.parser").prettify())
        # with open("food_data.txt", "w") as file:
        #     file.writelines([f'{item}\n' for item in data])
        if "برنامه غذایی معادل پیدا نشد" in text or "لطفا مقدار مناسب وارد کنید" in text:
            raise(NoSuchFoodSchedule)
        if "اعتبار شما کم است" in text:
            raise(NotEnoughCreditToReserve)
        self.remainCredit -= total_food_prices
        return self.remainCredit

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

    def get_reserve_table_foods(self, place_id: int) -> dict:
        """ output:
        {
            <date>: {
                <food_time>: {
                    food: <food_name>,
                    price: <price>,
                    food_id: <food_reserve_id>
                }
            }'
        }    
        """
        table = self.__load_food_table(place_id=place_id)
        # Save page.text to file
        # with open("out.html", "w") as file:
        #     file.write(bs(table.content, "html.parser").prettify())
        self.remainCredit = int(bs(table.content, "html.parser").find("span", {"id": "creditId"}).text)
        if table.status_code != HTTPStatus.OK:
            logging.debug("Something went wrong with status code: %s", table.status_code)
            return {}
        return self.__parse_reserve_table(table)

    def __setad_login(self) -> bool:
        logging.debug("Making session")
        self.session = requests.Session()
        logging.debug("Get login page")

        reserve_page = self.session.get(Dining.RESERVE_PAGE_URL)
        self.csrf = bs(reserve_page.content, "html.parser").find("input", {"name": "_csrf"}).get("value")
        data = {
            '_csrf': self.csrf,
            'username': self.student_id,
            'password': self.password,
            'login': 'ورود',
        }

        response = self.session.post('https://setad.dining.sharif.edu/j_security_check',  data=data)
        # with open("out.html", "w") as file:
        #     file.write(bs(response.content, "html.parser").prettify())

        script = bs(response.content, "html.parser").find("script", {"type": "text/javascript"}).next.strip()
        self.csrf = re.match(r".*X-CSRF-TOKEN' : '(?P<csrf>.*)'}.*", script).group("csrf")

        if response.status_code != HTTPStatus.OK:
            logging.debug("Login failed")
            return False
        return True

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

    def __load_food_table(self, place_id: str, week: int = 0) -> requests.Response:
        now = datetime.datetime.now()
        start_of_week = now - datetime.timedelta(days=(now.weekday() + 2) % 7) + datetime.timedelta(weeks=week)
        epoch_start_of_week = str(int(start_of_week.timestamp()) * 1000)
        # print(epoch_start_of_week)

        data = [
            ('weekStartDateTime', epoch_start_of_week),
            ('remainCredit', '0'),
            ('method:showNextWeek', 'Submit'),
            ('_csrf', self.csrf),
            ('selfChangeReserveId', ''),
            ('weekStartDateTimeAjx', epoch_start_of_week),
            ('freeRestaurant', 'false'),
            ('selectedSelfDefId', str(place_id)),
            ('_csrf', self.csrf),
        ]

        return self.session.post(Dining.RESERVE_FOOD_URL, data=data)
        # Save response text to out.html
        # with open("out.html", "w") as file:
        #    file.write(bs(response.content, "html.parser").prettify())

    def __parse_reserve_table(self, reserve_table: requests.Response) -> dict:
        content = bs(reserve_table.content, "html.parser").find("td", {"id": "pageTD"}).findNext("table").findNext(
            "table")
        self.meals = [static_data.MEAL_FA_TO_EN[time.text.split(("\n"))[1].strip()] for time in
                      content.findNext("tr").find_all("td")]
        content = content.find_all("tr", recursive=False)
        res = {}
        for i in range(1, len(content)):
            day, date = content[i].find_next("td").text.split("\n")[1].strip(), \
                content[i].find_next("td").text.split("\n")[3]
            time = f"{date} {day}"
            res[time] = {}
            content[i] = content[i].findNext("td")
            meal_food_counter = 0
            for j in range(len(self.meals)):
                res[time][self.meals[j]] = res[time].get(self.meals[j], [])
                if (len(content[i].findNext("td").findNext("table").find_all("tr", recursive=False)) != 0):
                    foods = content[i].findNext("td").findNext("table").find_all("tr", recursive=False)
                    for k in range(len(foods)):
                        price = foods[k].find_next("div", {"class": "xstooltip"}).text.split(
                            "\n")[2].strip()
                        food_name = foods[k].findNext("span").text.split("\n")[2].strip().split("|")[1].strip()
                        food_program_id = content[i].findNext("td").findNext("table").find_all("tr", recursive=False)[
                            meal_food_counter].find_next(
                            "div", {"class": "xstooltip"}).get("id").split("_")[-1].strip()

                        inputs = list(content[i].findNext("td").findAll("input"))
                        if meal_food_counter == 0: inputs.reverse()
                        for input in inputs:
                            if input.attrs.get('type') == "checkbox":
                                food_id =  input.attrs['foodid']
                                food_program_date = input.attrs['programdate']
                                food_type_id = input.attrs['foodtypeid']
                        res[time][self.meals[j]].append({
                            "food": food_name,
                            "price": price,
                            "program_id": food_program_id,
                            "food_id": food_id,
                            "program_date": food_program_date,
                            "food_type_id": food_type_id
                        })
                        meal_food_counter += 1
                content[i] = content[i].findNext("td")
        foods = dict(reversed(list(res.items())))
        return foods

    def __parse_food_table_to_get_foods_list(self, table: requests.Response) -> list:
        content = bs(table.content, "html.parser")
        # with open("content.html", "w") as file:
        #     file.write(str(content))
        foods = content.find("table").find_all("span")[2:]
        result = []
        for food in foods:
            food_name = food.text.strip().split("|")[1].strip()
            result.append(food_name.strip())
        return result

    def __parse_reserve_page_to_get_food_courts(self, reserve_page: requests.Response) -> dict:
        """
        output:
        {
            "food_court_name": <str>,
            "food_coutn_id": <str>
        }
        """
        content = bs(reserve_page.content, "html.parser")
        food_courts = {}
        for option in content.find_all("option", recursive=True):
            if option.attrs.get("value"):
                food_courts[" - ".join([ part.strip() for part in option.text.split("-")[:-1] ])] = option.attrs.get("value")
        return food_courts

    def get_user_food_courts(self):
        response = self.session.get(Dining.SHOW_PANEL_URL)
        return self.__parse_reserve_page_to_get_food_courts(response)
