import src.static_data as static_data
from src.messages import code_statistics_message, no_code_for_today_message, no_available_code_for_today_message

def seprate_admins(admins: str) -> list:
    return set([int(admin_id) for admin_id in admins.split('\\n')])

def get_food_court_id_by_name(food_court: str) -> int:
    return static_data.FOOD_COURT_IDS.get(food_court)

def get_food_court_name_by_id(food_court_id) -> str:
    for key, value in static_data.FOOD_COURT_IDS.items():
        if value == int(food_court_id):
            return key

def make_forget_code_statistics_message(forget_codes: tuple) -> str:
    used, unused = [list(l) for l in forget_codes]
    used_forget_codes_list = "\n".join(["{}: {}".format(
        get_food_court_name_by_id(forget_code.get("_id")), forget_code.get("count")) 
        for forget_code in used])
    unused_forget_codes_list = "\n".join(["{}: {}".format(
        get_food_court_name_by_id(forget_code.get("_id")), forget_code.get("count")) 
        for forget_code in unused])
    return code_statistics_message.format(
        used_forget_codes_list if used_forget_codes_list else no_code_for_today_message,
        unused_forget_codes_list if unused_forget_codes_list else no_available_code_for_today_message)
