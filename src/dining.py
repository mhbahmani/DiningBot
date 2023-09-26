from bs4 import BeautifulSoup as bs
from http import HTTPStatus
from src.error_handlers import ErrorHandler
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

    def reserve_food(self, place_id: int, food_id: str, foods: dict, choosed_food_indices: dict) -> bool:
        """
        food: {
            food: <food_name>,
            price: <price>,
            food_id: <food_reserve_id>,
            program_id: <food_program_id>,
            program_date: <food_program_date>
        }
        """
        logging.debug("Reserving food %s", food_id)
        now = datetime.datetime.now()
        start_of_week = now - datetime.timedelta(days=now.weekday() + 2)
        epoch_start_of_week = int(start_of_week.timestamp()) * 1000
        epoch_end_of_week = int((start_of_week + datetime.timedelta(days=7)).timestamp()) * 1000

        data = [
            ('weekStartDateTime', '1695414600000'),
            ('remainCredit', '-300000'),
            ('method:doReserve', 'Submit'),
            ('_csrf', self.csrf),
            ('selfChangeReserveId', ''),
            ('weekStartDateTimeAjx', epoch_start_of_week),
            ('freeRestaurant', 'false'),
            ('selectedSelfDefId', '1'),
        ]

        i = 0
        for day in foods:
            for meal in foods[day]:
                for food_index, food in enumerate(foods[day][meal]):
                    food_data = []
                    if food_index == choosed_food_indices[day][meal]:
                        food_data += [(f"userWeekReserves[{i}].selected", 'true')]
                    food_data += [
                        (f"userWeekReserves[{i}].selectedCount", '1'),
                        (f"userWeekReserves[{i}].id", ''),
                        (f"userWeekReserves[{i}].programId", food.get("program_id")),
                        (f"userWeekReserves[{i}].mealTypeId", '1'),
                        (f"userWeekReserves[{i}].programDateTime", '1695587400000'), # Food day
                        (f"userWeekReserves[{i}].selfId", str(place_id)),
                        (f"userWeekReserves[{i}].foodTypeId", '644'),
                        (f"userWeekReserves[{i}].foodId", food.get("food_id")),
                        (f"userWeekReserves[{i}].priorReserveDateStr", f'{food.get("program_date")} 08:00:00.0'),
                        (f"userWeekReserves[{i}].freeFoodSelected", 'false'),
                    ]
                    data += food_data
                    i += 1
        response = self.session.post(Dining.RESERVE_FOOD_URL, data=data)
        text = bs(response.content, "html.parser").prettify()
        with open("out.html", "w") as file:
            file.write(bs(response.content, "html.parser").prettify())
        if "برنامه غذایی معادل پیدا نشد" in text:
            return False, 0
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
            }'
        }    
        """
        table = self.__load_food_table(place_id=place_id, week=week)
        # Save page.text to file
        with open("out.html", "w") as file:
            file.write(bs(table.content, "html.parser").prettify())
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

    def __load_food_table(self, place_id: int, week: int = 1) -> requests.Response:
        now = datetime.datetime.now()
        start_of_week = now - datetime.timedelta(days=(now.weekday() + 2) % 7)
        epoch_start_of_week = int(start_of_week.timestamp()) * 1000
        # print(epoch_start_of_week)

        data = [
            ('weekStartDateTime', '1694874869301'),
            ('remainCredit', '0'),
            ('method:showNextWeek', 'Submit'),
            ('_csrf', self.csrf),
            ('selfChangeReserveId', ''),
            ('weekStartDateTimeAjx', epoch_start_of_week),
            ('freeRestaurant', 'false'),
            ('selectedSelfDefId', '1'),
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
            for j in range(len(self.meals)):
                res[time][self.meals[j]] = res[time].get(self.meals[j], [])
                if (len(content[i].findNext("td").findNext("table").find_all("tr", recursive=False)) != 0):
                    foods = content[i].findNext("td").findNext("table").find_all("tr", recursive=False)
                    for k in range(len(foods)):
                        price = foods[k].find_next("div", {"class": "xstooltip"}).text.split(
                            "\n")[2].strip()
                        food_name = foods[k].findNext("span").text.split("\n")[2].strip().split("|")[1].strip()
                        food_program_id = content[i].findNext("td").findNext("table").find_all("tr", recursive=False)[
                            0].find_next(
                            "div", {"class": "xstooltip"}).get("id").split("_")[-1].strip()
                        # <input foodid="30" foodtypeid="644" id="userWeekReserves.selected3" mealtypeid="1" name="userWeekReserves[3].selected" onclick="enableDisableNumber(this, 'userWeekReserves.selectedCount3', '100000', 'hiddenSelectedCount3', new Array( 'userWeekReserves.selected3'), new Array( 'userWeekReserves.selectedCount3'), '1', '1',null,null,1);" programdate="2023-09-27" type="checkbox" value="true"/>
                        food_id =  content[i].findNext("td").find("input").attrs['foodid']
                        food_program_date = content[i].findNext("td").find("input").attrs['programdate']
                        res[time][self.meals[j]].append({
                            "food": food_name,
                            "price": price,
                            "program_id": food_program_id,
                            "food_id": food_id,
                            "program_date": food_program_date
                        })
                content[i] = content[i].findNext("td")
        foods = dict(reversed(list(res.items())))
        return foods

    def __parse_food_table_to_get_foods_list(self, table: requests.Response) -> list:
        content = bs(table.content, "html.parser")
        with open("content.html", "w") as file:
            file.write(str(content))
        foods = content.find("table").find_all("span")[2:]
        result = []
        for food in foods:
            food_name = food.text.strip().split("|")[1].strip()
            result.append(food_name.strip())
        return result

    def __parse_reserve_page_to_get_food_courts(self, reserve_page: requests.Response) -> dict:
        content = bs(reserve_page.content, "html.parser")
        return dict(map(lambda x: (x.getText(), x.attrs["value"]), content.find_all("option")))

    def get_user_food_courts(self):
        response = self.session.get(Dining.RESERVE_PAGE_URL)
        return self.__parse_reserve_page_to_get_food_courts(response)
