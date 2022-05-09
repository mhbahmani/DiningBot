import src.static_data as static_data


def seprate_admins(admins: str) -> list:
    return set([int(admin_id) for admin_id in admins.split('\\n')])

def get_food_court_id_by_name(food_court: str) -> int:
    return static_data.FOOD_COURT_IDS.get(food_court)