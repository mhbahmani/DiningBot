def seprate_admins(admins: str) -> list:
    return [int(admin_id) for admin_id in admins.split('\\n')]
