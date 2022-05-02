start_message = "غذا می‌قولی؟!"

help_message = """
/set <student_number> <password>
/help: مشاهده‌ی راهنما
"""

admin_help_message = """
دستورات کاربران:
{}

دستورات ادمین (این بخش به کاربران عادی نمایش داده نمی‌شود)

""".format(help_message)

set_wrong_args_message = """اشتباه زدی. بعد از /set دو تا مقدار باید بذاری، اولی شماره‌دانشجویی، دومی رمز عبور.

این شکلی:
/set 97102111 thisismypassword1234"""

set_result_message = """اطلاعاتی که بهم دادی:
شماره دانشجویی: {}
رمز عبور: {}"""