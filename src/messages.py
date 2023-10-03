# TODO: Store messages in a database!

start_message = """
🍕 غذا می‌قولی؟!

از قسمت «رزرو غذا» می‌تونی رزرو خودکار غذا رو فعال کنی.
روی /help کلیک کن تا توضیحات کامل‌تر رو ببینی 
"""

main_menu_message = "از منویی که این پایین هست انتخاب کن که چی می‌خوای"
forget_code_menu_message = "ازین پایین چیزی که می‌خوای رو پیدا کن" # TODO
reserve_menu_messsage = "منوی رزرو" # TODO

details_message = """
توضیحات مربوط به انتخاب اولویت‌ها:
"""

# help_message = """
# /set <student_number> <password> :‌ تنظیم شماره‌ی دانشجویی و رمز عبور داینینگ
# /help: مشاهده‌ی راهنما
# """

help_message = """
سلام!✋🏻 همونطور که قول داده بودم، قابلیت رزرو اتوماتیک غذا به بات اضافه شد! 🥳

🟢 از طریق بخش «رزرو غذا» توی منوی اصلی می‌تونی منوی این بخش رو ببینی.

✅ سیستم اینطوریه که شماره دانشجویی و پسوردت رو تو قسمت «تنظیم نام کاربری و رمز عبور» برای ورود به سایت داینینگ باید بهم بدی.

✅ بعد از اون، می‌تونی تو قسمت «انتخاب غذاهای مورد علاقه»، غذاهایی که دوس داری رو به ترتیب اولویت مشخص کنی. من این ترتیب رو نگه می‌دارم، تا هر وقت تو یه روز دو تا غذا برای رزرو وجود داشت، بتونم یکی رو برات بگیرم. البته لازم نیست همه‌ی غذاها رو انتخاب کنی، می‌تونی فقط چنتا غذا رو که بیشتر از بقیه دوس داری بهم بگی، تا مطمئن بشی اونارو برات رزرو می‌کنم. اگه اولویتی بین دو تا غذا انتخاب نکرده باشی، به طور تصادفی یکی رو برات رزرو می‌کنم.

✅ حالا، با زدن دکمه‌ی «فعال کردن رزرو خودکار»، بهم می‌گی که از این به بعد رزرو غذا رو برات انجام بدم. وقتی روی این دکمه کلیک کنی، بعد چن ثانیه، لیست سلف‌هایی که تو می‌تونی ازشون غذا بگیری بهت نشون داده می‌شه که می‌تونی با کلیک کردن روی هر کدوم، سلف‌هایی که می‌خوای ازشون برات غذا بگیرم رو مشخص کنی. بعد از این که سلف‌ها رو انتخاب کردی، روی دکمه‌ی «حله» کلیک می‌کنی و دیگه همه چی خوبه :)

🟢 من هر هفته، دوشنبه و سه‌شنبه و چهارشنبه حوالی ساعت ۸ شب غذا رزرو می‌کنم، قبلش هم یه خبر می‌دم بهت که اعتبار اکانتت رو چک کنی که یه وقت توی خرید مشکلی پیش نیاد. بعد از رزرو هم، نتیجه رو بهت اعلام می‌کنم.

🟢 اگه مشکلی تو رزروت بود بهت می‌گم که یه وقت بی‌غذا نمونی. اگه هر مشکلی پیش اومد، به ادمین اطلاع بده تا چک کنه. تو هفته‌های اول هم حتما خودت یه چک بکن که غذات درست رزرو شده باشه. نگی نگفتیااا :)
"""

# help_message = """
# هر جا گیر کردی /start بزن بیای منوی اول"""

admin_help_message = """
دستورات کاربران:
{}

دستورات ادمین (این بخش به کاربران عادی نمایش داده نمی‌شود)
/update_foods: به‌روزرسانی غذاها
""".format(help_message)

set_wrong_args_message = """اشتباه زدی. بعد از /set دو تا مقدار باید بذاری، اولی شماره‌دانشجویی، دومی رمز عبور.

این شکلی:
/set 97102111 thisismypassword1234"""

set_result_message = """
✅ اطلاعاتی که بهم دادی: 

👤 شماره دانشجویی: {}
🔑 رمز عبور: {}

اگه اشتباه زدی، دوباره بزن.
"""

update_food_list_result = """
🍟 {} غذای جدید پیدا شد!
"""

next_page_button_message = "< صفحه‌ی بعد"
previous_page_button_message = "صفحه‌ی قبل >"
done_button_message = "حله"
cancel_button_message = "لغو"
deactivate_button_message = "غیرفعال کردن رزرو خودکار"
change_food_courts_button_message = "تغییر سلف‌(ها)"

choose_food_priorities_message = """
به ترتیب علاقت، روی غذایی که می‌خوای کلیک کن. می‌تونی تو صفحه‌ی های دیگه هم دنبال غذاها بگردی 🍟
اگه سلف واسه یه روز دو تا غذا می‌داد، بر اساس این اولویت‌ها، برای یکی رو انتخاب می‌کنم. اگه هم اولویتت بین اون دو تا غذا رو مشخص نکرده باشی، رندم یکی رو برات رزرو می‌کنم.
نیازی نیست روی همه‌ی غذاها هم کلیک کنی.

هر وقت انتخابت تموم شد، روی «حله» کلیک کن تا لیست غذاهات ثبت بشه و هر وقت منصرف شدی، روی «لغو» کلیک کن تا تغییراتت کنسل بشن 🍗
"""
choosing_food_priorities_done_message = """
غذاهای مورد علاقت به ترتیبی که گفتی (تو پیامای این زیر این پیام هم می‌تونی ببینیشون) انتخاب شد. 🍻
می‌تونی دوباره روی «انتخاب غذاهای مورد علاقه» کلیک کنی تا از اول مورد علاقه‌هاتو مشخص کنی.
"""
choosing_food_priorities_cancel_message = """
لغو شد.
"""

choose_food_court_message_to_get = "کدوم سلف می‌خوای غذا بخوری؟"
choose_food_court_message_to_give = """دمت خیلی گرمه :))
کد فراموشیت برای کدوم سلفه؟"""

get_forget_code_from_user_message = "حالا لطفا کد فراموشیت رو برام بفرست"

not_int_code_error_message = "این چیه دیگه؟ کد بده بهم، کد فراموشی کلش باید عدد باشه"
not_enough_number_error_message = """کد فراموشی می‌تونه ۶ یا ۷ رقمی باشه
یه چک بکن ببین کجاشو اشتباه زدی، دوباره بفرست"""
food_court_not_choosed_error_message = "سلف رو هنوز انتخاب نکردی که، انتخاب کن"
forget_code_added_message = "دمت گرم. خدا خیرت بده :)"
get_food_name_message = "عیول، فقط بی‌زحمت بگو غذاش چیه؟ اگه نمی‌دونی هم بگو نمی‌دونم :)"

no_code_for_this_food_court_message = "متاسفم، ولی کسی کد فراموشی واسه این سلف نذاشته :("
forget_code_founded_message = """یه کد برات پیدا کردم! :)
برو بزن به بدن، عشق کن. اینم کد:
{} - {} - {}

🍽 دم @{} هم گرم که این کد رو گذاشته
اگه خواستی ازش تشکر کن، منم براش یه پیام فرستادم و تشکر کردم :)
"""
code_statistics_message = """
کد مد چه خبر؟

کل کدهای امروز:
{}

کدهای قابل دریافت:
{}
"""
no_code_for_today_message = """
امروز هیچی کد ثبت نشده🥲
ایناس که بده!"""
no_available_code_for_today_message = """فعلا کدی که گرفته نشده باشه ندارم🥲"""
someone_took_your_code_message = "غرض از مزاحمت، یه نفر کدت رو گرفت! ممنون که کدت رو گذاشتی تو بات."

still_under_struction = """
با توجه به تغییراتی که سایت داینینگ کرده، این بخش باید تغییراتی توش به وجود بیاد و فعلا قابل استفاده نیست.

اگر مایل به کمک توی توسعه‌ی بات هستید، حتما بهم پیام بدید."""

new_user_message = """
@{} اومد تو
"""

users_ranking_message = """
۵۰ نفری که بیشتر از بقیه کد فراموشی اهدا کردن:

{}

رتبه‌بندی هر چند دقیقه آپدیت می‌شه""" 

ranking_message = "🍔 {}- {}: {}\n" 
user_rank_message = "\nرتبه‌ی تو: {} از {} نفر"

no_one_added_code_yet_message = """
متاسفانه هنوز کسی کدی اضافه نکرده 🥲
ایناس که بده!

رتبه‌بندی هر چند دقیقه آپدیت می‌شه""" 

i_dont_want_this_code_message = """
این کد رو نمی‌خوام
"""
forget_taked_back_message = """
ممنون، کد تحویل گرفته شد"""
rank_not_found_message = """نمی‌دونم 🥶"""

restart_bot_message = "بات تو این مدتی که بهش سر نزدی یه بار ری‌استارت شده. برات آپدیت کردم باتو، لطفا دوباره از منوی پایین چیزی که می‌خوای رو انتخاب کن!"
fake_forget_code_report_message = "عه کد چرت دادن بهت؟ :( لطفا بگو که کدش چی بوده تا پیگیری کنم"
fake_forget_code_taked_message = "حله. ممنونم که اطلاع دادی و متاسفم بابت این اتفاق"
# fake_forget_code_taked_message = """
# حله. ممنونم که اطلاع دادی و متاسفم بابت این اتفاق
# این کد رو {} ثبت کرده بود. احتمالا یه اشتباه جزئی کرده تو وارد کردن کد."""

you_already_have_forget_code_message = "ببین یه دونه کد دیگه امروز گرفتی، اگه اونو نمی‌خوای، دکمه‌ی زیرش رو بزن، بعد واسه کد جدید درخواست بده."

update_foods_started_message = "🔍 آپدیت لیست غذاها آغاز شد"
no_food_found_message = "هیچ غذایی تو جدول رزرو پیدا نکردم 🤔"

choose_food_courts_to_automatic_reserve_message = "از بین سلف‌های پایین، سلف‌هایی که می‌خوای براشون اتوماتیک غذا رزرو بشه رو انتخاب کن"
no_food_court_choosed_message = """هیج سلفی رو انتخاب نکردی. اگه پشیمون شدی، روی لغو کلیک کن یا اگه می‌خوای ادامه بدی، اول سلف‌هایی که می‌خوای رو انتخاب کن، بعد روی حله کلیک کن."""
food_court_not_found_message = "این سلفی که زدی رو نمی‌شناسم. لطفا به ادمین بگو"
no_user_info_message = "هنوز شماره دانشجویی و رمز عبورت رو بهم ندادی. از منوی رزرو، بخش تنظیم مشخصات، این اطلاعاتو بهم بده تا بتونم برات غذا رزرو کنم"
activate_automatic_reserve_started_message = "هممم، چند لحظه صبر کن"
choosing_food_courts_done_message = ".حله. از این به بعد، هر هفته سه‌شنبه شب‌ها، غذا برای سلف‌هایی که انتخاب کردی، بر اساس اولویت‌های که بهم گفتی رزرو می‌شه"
choosing_food_courts_cancel_message = "لغو شد"
automatic_reserve_already_activated_message = "رزرو خودکار قبلا برات فعال شده. از بین گزینه‌های پایین انتخاب کن که می‌خوای چیکار کنی."
automatic_reserve_deactivated_message = "رزرو خودکار غیر فعال شد"

get_username_message = "لطفا شماره دانشجوییت رو بهم بگو"
get_password_message = "لطفا رمز عبورت رو هم بهم بگو"
login_info_already_set_message = "نام کاربری و رمز عبورت رو قبلا تنظیم کردی. اگه می‌خوای عوضشون کنی، ادامه بده."
username_and_password_saved_message = "رواله. بذار یه چک بکنم ببینم اطلاعاتی که دادی درسته یا نه. الان خبرت می‌کنم."
username_or_password_incorrect_message = "❌ با این مشخصاتی که دادی نتونستم وارد سایت بشم. یه چک بکن چیزایی که وارد کردی رو و دوباره روی گزینه‌ی تنظیم مشخصات کلیک کن."
username_and_password_correct_message = "✅ اطلاعاتت درست بود و تونستم وارد سایت بشم"

reserve_was_secceeded_message = """
غذای هفته‌ی بعدت توی «{}» رزرو شد.

{}

اعتبار اکانتت: {}
یه چک بکن همه چی درست باشه. اگه مشکلی بود بهم بگو
"""
reserve_was_failed_message = """یه مشکلی توی رزرو غذای هفته‌ی بعدت توی «{}» به وجود اومد. لطفا یه سر به سایت داینینگ بزن و چک کن غذایی رزرو نشده باشه، یا این که به اندازه‌ی کافی موجودی داشته باشی.
من دوشنبه، سه‌شنبه و چهارشنبه شب‌ها غذا رزرو می‌کنم، پس اگه امروز چهارشنبه نیست، من فردا شب بازم سعی می‌کنم برات غذا بگیرم. ولی اگه امروز چهارشنبه‌ست، دیگه من غذا نمی‌گیرم و باید خودت غذا بگیری."""
list_reserved_foods_message = "🌭 {} - {}: {}"
automatic_reserve_notification_message = "۲ ساعت دیگه غذای هفته‌ی بعد رزرو می‌شه. یه چک بکن حداقل ۲۰ تومن توی اکانتت اعتبار داشته باشی."
no_food_for_reserve_message = "توی {} غذایی واسه رزرو کردن نیست🤔. یا خودت قبلا رزرو کردی، یا توی این سلف هفته‌ی دیگه غذا نمی‌دن. اگه به نظرت مشکلی پیش اومده به ادمین بگو."
you_dont_have_food_for_next_week_message = """خواستم بگم غذای هفته‌ی بعدت احتمالا به خاطر این که تو سه روز گذشته اعتبار نداشته اکانتت، رزرو نشده\. گشنه نمونی :\) برو غذاتو رزرو کن

🔗 [سایت داینینگ](http://dining.sharif.ir)"""

send_to_all_done_message = "پیامت برای همه با موفقیت ارسال شد :)"

not_allowed_to_reserve_message = "داینینگ بهت امکان رزرو غذا رو نداده. چک کن که بخش رزرو غذا توی داینینگ برات باز باشه"

duplicate_forget_code_message = "این کد قبلا وارد شده و امکان ۲ بار وارد کردن یه کد یکسان وجود نداره."

you_are_not_admin_message = "ای کلک! متاسفم ولی این کامند فقط برای ادمینه :)"

not_enough_credit_to_reserve_message = """سلام، اکانتت اعتبار کافی برای رزرو غذای هفته‌ی آینده‌ت توی **{}** رو نداره. اگه امروز چهارشنبه نیست، با شارژ کردن اکانتت، فردا برات غذا می‌گیرم. ولی اگه امروز چهارشنبه‌س، دیگه خودت باید غذای این هفته رو رزرو کنی."""