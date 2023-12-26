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

class FoodsCapacityIsOver(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "FoodsCapacityIsOver"
        super().__init__(message, *args)

class DiningConnectionError(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "Can not connect to dining"
        super().__init__(message, *args)

class NoFoodScheduleForUser(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "NoFoodScheduleForUser"
        super().__init__(message, *args)


class DiningLoginFailed(BaseException):
    def __init__(self, *args: object, message=None) -> None:
        message = message if message else "DiningLoginFailed"
        super().__init__(message, *args)
