# DiningBot 🍔🤖

The DiningBot is a Telegram bot designed to facilitate the process of reserving and accessing foods from the Sharif University's food courts. The bot consists of two main parts. In the first part, users can take "forget codes" that other users gave. They can also give away "forget codes" if they don't want their reserved meal. In the second part, users can set their preferences for different foods and select the weekdays they want to reserve food. The bot then automatically reserves food for them each week based on their preferences.

## Setup and Run
```bash
echo 'db.bot_users.createIndex({"user_id": 1}, {unique: true})' | mongo diningbotdb

pip install -r requirements

python main.py
python garbage_collector_main.py
python automatic_reserve_main.py
```

### __Welcome to Contribute__
Contributions are welcome! If you would like to contribute to this project, feel free to submit a pull request.
