PLACES = {
    "مرکزی - سلف دانشجویان آقا": "19",
    "خوابگاه - طرشت 3": "21",
    "خوابگاه - شهید احمدی روشن": "22",
    # "خوابگاه - مصلی نژاد": "24",
    # "خوابگاه - شهید وزوایی": "25",
    # "خوابگاه - شادمان": "26",
    # "خوابگاه - آزادی": "28",
    # "خوابگاه - 12واحدی": "29",
    # "خوابگاه - ولیعصر": "30",
    # "خوابگاه - درویشوند": "55",
    # "رستوران های مکمل - سلف آزاد - دنا": "58",
    # "رستوران های مکمل - سلف آزاد - لاله": "59"
}

FOOD_COURT_IDS = {
    "سلف پسرها": 1,
    "سلف دخترها": 2,
    "احمدی روشن": 3,
    'طرشت ۲': 4,
    'طرشت ۳': 5,
    'مصلی نژاد': 6,
    'آزادی': 7,
    'شهید شوریده': 8,
    'شهید وزوایی': 9,
    'شهید حیدرتاش': 10,
    'شهید صادقی': 11,
    'شادمان': 12,
    'ولیعصر': 13,
    'شهرک': 14,
    'درویش‌وند': 15
}

# Stages
MAIN_MENU_CHOOSING, FORGET_CODE_MENU_CHOOSING, RESERVE_MENU_CHOOSING, CHOOSING_SELF_TO_GET, CHOOSING_SELF_TO_GIVE, INPUT_FOOD_NAME, INPUT_FORGET_CODE, INPUT_FAKE_FORGET_CODE = range(8)

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

SET_FAVORITES_LABEL = "Set Favorites"
SET_FAVORITES_REGEX = '^{}$'.format(SET_FAVORITES_LABEL)
RESERVE_LABEL = "Reserve"
RESERVE_REGEX = '^{}$'.format(RESERVE_LABEL)

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
RESERVE_MENU_CHOICES = [
    ['Reserve', 'Set Favorites'],
    [BACK_TO_MAIN_MENU_LABEL]
]

SELFS = [
    ['سلف پسرها', 'سلف دخترها'],
    ['احمدی روشن', 'طرشت ۲', 'طرشت ۳'],
    ['مصلی نژاد', 'آزادی', 'شهید شوریده'],
    ['شهید وزوایی', 'شهید حیدرتاش', 'شهید صادقی'],
    ['شادمان', 'ولیعصر', 'شهرک'],
    ['درویش‌وند'],
    [BACK_TO_MAIN_MENU_LABEL]
]

FOOD_COURTS_REGEX = "^(درویش‌وند|شادمان|ولیعصر|شهرک|شهید وزوایی|شهید حیدرتاش|شهید صادقی|مصلی نژاد|آزادی|شهید شوریده|احمدی روشن|طرشت ۲|طرشت ۳|سلف پسرها|سلف دخترها)$"
INPUT_FORGET_CODE_EXCLUDE = f'^({BACK_TO_MAIN_MENU_LABEL}|درویش‌وند|شادمان|ولیعصر|شهرک|شهید وزوایی|شهید حیدرتاش|شهید صادقی|مصلی نژاد|آزادی|شهید شوریده|احمدی روشن|طرشت ۲|طرشت ۳|سلف پسرها|سلف دخترها)$'