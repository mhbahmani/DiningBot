class BaseException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)


class NotEnoughCreditToReserve(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "NotEnoughCreditToReserve"
        super().__init__(message, *args)

class NoSuchFoodSchedule(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "NoSuchFoodSchedule"
        super().__init__(message, *args)

class AlreadyReserved(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "AlreadyReserved"
        super().__init__(message, *args)
