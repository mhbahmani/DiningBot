# TODO: Get this places from an database
# TODO: Update Places automaticly
PLACES = {
    "مرکزی - سلف دانشجویان آقا": "1",
    "مرکزی - سلف دانشجویان خانم": "2",
    "خوابگاه - طرشت 3": "3",
    "خوابگاه - شهید احمدی روشن": "11",
    "خوابگاه - طرشت 2 (خواهران)": "12",
    "خوابگاه - مصلی نژاد": "10",
    "خوابگاه - شهید وزوایی": "13",
    "خوابگاه - شادمان": "6",
    "خوابگاه - شهید شوریده (خواهران)": "7",
    "خوابگاه - آزادی": "8",
    "خوابگاه - حیدرتاش": "9",
    "خوابگاه - ولیعصر": "14",
    # "خوابگاه - درویشوند": "55",
    # "رستوران های مکمل - سلف آزاد - دنا": "58",
    # "رستوران های مکمل - سلف آزاد - لاله": "59"
}

PLACES_NAME_BY_ID = {
    "1": "مرکزی - سلف دانشجویان آقا",
    "2": "مرکزی - سلف دانشجویان خانم",
    "3": "خوابگاه - طرشت 3",
    "11": "خوابگاه - شهید احمدی روشن",
    "12": "خوابگاه - طرشت 2 (خواهران)",
    "10": "خوابگاه - مصلی نژاد",
    "13": "خوابگاه - شهید وزوایی",
    "6": "خوابگاه - شادمان",
    "7": "خوابگاه - شهید شوریده (خواهران)",
    "8": "خوابگاه - آزادی",
    "14": "خوابگاه - ولیعصر",
    "9": "ﺥﻭﺎﺑگﺎﻫ - ﺡیﺩﺮﺗﺎﺷ",
    # "55": "خوابگاه - درویشوند",
    # "58": "رستوران های مکمل - سلف آزاد - دنا",
    # "59": "رستوران های مکمل - سلف آزاد - لاله"
}

FOOD_COURT_IDS = {
    "سلف پسرها": 1,
    "سلف دخترها": 2,
    "احمدی روشن": 11,
    "طرشت ۲": 4,
    "طرشت ۳": 3,
    "مصلی نژاد": 10,
    "آزادی": 8,
    "شهید شوریده": 7,
    "شهید وزوایی": 13,
    "شهید حیدرتاش": 9,
    "شادمان": 6,
    "ولیعصر": 14,
    # 'شهرک': 5,
    # 'درویش‌وند': 15
}

MEAL_FA_TO_EN = {
    "ناهار": "lunch",
    "شام": "dinner",
    "سحری": "sahari",
    "افطاری": "eftari",
    "صبحانه": "breakfast"
}

MEAL_EN_TO_FA = {
    "lunch": "ناهار",
    "dinner": "شام",
    "sahari": "سحری",
    "eftari": "افطار"
}

# Stages
MAIN_MENU_CHOOSING, FORGET_CODE_MENU_CHOOSING, RESERVE_MENU_CHOOSING, \
    CHOOSING_SELF_TO_GET, CHOOSING_SELF_TO_GIVE, INPUT_FOOD_NAME, \
        INPUT_FORGET_CODE, INPUT_FAKE_FORGET_CODE, INPUT_USERNAME, \
            INPUT_PASSWORD, CHOOSE_RESERVE_DAYS_FOOD_COURT, CHOOSE_RESERVE_DAYS = range(12)

FORGET_CODE_MENU_LABEL = 'کد فراموشی'
FORGET_CODE_MENU_REGEX = '^{}$'.format(FORGET_CODE_MENU_LABEL)

RESERVE_MENU_LABEL = 'رزرو غذا'
RESERVE_MENU_REGEX = '^{}$'.format(RESERVE_MENU_LABEL)

RANKING_FORGET_CODE_LABLE = "بیشترین کد دهندگان"
RANKING_FORGET_CODE_REGEX = '^{}$'.format(RANKING_FORGET_CODE_LABLE)
GET_FORGET_CODE_LABEL = "یه کد بده که بدجور گشنمه"
GET_FORGET_CODE_REGEX = '^{}$'.format(GET_FORGET_CODE_LABEL)
GIVE_FORGET_CODE_LABEL = "می‌خوام یه کد بدم عشق کنی"
GIVE_FORGET_CODE_REGEX = '^{}$'.format(GIVE_FORGET_CODE_LABEL)
BACK_TO_MAIN_MENU_LABEL = "برگردیم همون اول"
BACK_TO_MAIN_MENU_REGEX = '^{}$'.format(BACK_TO_MAIN_MENU_LABEL)
FAKE_FORGET_CODE_LABLE = "گزارش کد الکی"
FAKE_FORGET_CODE_REGEX = '^{}$'.format(FAKE_FORGET_CODE_LABLE)
TODAY_CODE_STATISTICS_LABEL = "گزارش کدهای امروز"
TODAY_CODE_STATISTICS_REGEX = '^{}$'.format(TODAY_CODE_STATISTICS_LABEL)

SET_FAVORITES_LABEL = "انتخاب غذاهای مورد علاقه"
SET_FAVORITES_REGEX = '^{}$'.format(SET_FAVORITES_LABEL)
SHOW_FAVORITES_LABEL = "نمایش غذاهای مورد علاقه"
SHOW_FAVORITES_REGEX = '^{}$'.format(SHOW_FAVORITES_LABEL)
RESERVE_LABEL = "رزرو غذا"
RESERVE_REGEX = '^{}$'.format(RESERVE_LABEL)
SET_USERNAME_AND_PASSWORD_LABEL = "تنظیم نام کاربری و رمز عبور"
SET_USERNAME_AND_PASSWORD_REGEX = '^{}$'.format(SET_USERNAME_AND_PASSWORD_LABEL)
CHOOSE_DAYS_LABEL = "انتخاب روزهایی ک غذا می‌خوای"
CHOOSE_DAYS_REGEX = '^{}$'.format(CHOOSE_DAYS_LABEL)
ACTIVATE_AUTOMATIC_RESERVE_LABEL = "فعال کردن رزرو خودکار"
ACTIVATE_AUTOMATIC_RESERVE_REGEX = '^{}$'.format(ACTIVATE_AUTOMATIC_RESERVE_LABEL)

MAIN_MENU_CHOICES = [
    [FORGET_CODE_MENU_LABEL, RESERVE_MENU_LABEL]
]
BACK_TO_MAIN_MENU_CHOICES = [
    [BACK_TO_MAIN_MENU_LABEL]
]
FORGET_CODE_MENU_CHOICES = [
    [GET_FORGET_CODE_LABEL, GIVE_FORGET_CODE_LABEL],
    [RANKING_FORGET_CODE_LABLE, FAKE_FORGET_CODE_LABLE, TODAY_CODE_STATISTICS_LABEL],
    [BACK_TO_MAIN_MENU_LABEL]
]
# TODO: Add RESERVE_LABEL to RESERVE_MENU_CHOICES
RESERVE_MENU_CHOICES = [
    [SET_USERNAME_AND_PASSWORD_LABEL, ACTIVATE_AUTOMATIC_RESERVE_LABEL],
    [SET_FAVORITES_LABEL, SHOW_FAVORITES_LABEL, CHOOSE_DAYS_LABEL],
    [BACK_TO_MAIN_MENU_LABEL]
]

SELFS = [
    ['سلف پسرها', 'سلف دخترها'],
    ['احمدی روشن', 'طرشت ۲', 'طرشت ۳'],
    ['مصلی نژاد', 'آزادی', 'شهید شوریده'],
    ['شهید وزوایی', 'شهید حیدرتاش', 'شهید صادقی'],
    ['شادمان', 'ولیعصر'],
    # ['شادمان', 'ولیعصر', 'شهرک'],
    # ['درویش‌وند'],
    [BACK_TO_MAIN_MENU_LABEL]
]

FOOD_COURTS_REGEX = "^(درویش‌وند|شادمان|ولیعصر|شهرک|شهید وزوایی|شهید حیدرتاش|شهید صادقی|مصلی نژاد|آزادی|شهید شوریده|احمدی روشن|طرشت ۲|طرشت ۳|سلف پسرها|سلف دخترها)$"
INPUT_FORGET_CODE_EXCLUDE = f'^({BACK_TO_MAIN_MENU_LABEL}|درویش‌وند|شادمان|ولیعصر|شهرک|شهید وزوایی|شهید حیدرتاش|شهید صادقی|مصلی نژاد|آزادی|شهید شوریده|احمدی روشن|طرشت ۲|طرشت ۳|سلف پسرها|سلف دخترها)$'

INPUT_USERNAME_AND_PASSWORD_EXCLUDE = f'^{BACK_TO_MAIN_MENU_LABEL}$'
