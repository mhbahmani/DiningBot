from src.error_handlers import ErrorHandler


class Samad:
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

    def __samad_login(self) -> bool:
        # TODO
        pass

    def check_username_and_password(username: str, password: str) -> bool:
        # TODO
        pass