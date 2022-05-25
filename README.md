# DiningBot
A telegram bot for reserving food and sharing food forget code between sharif students.  
  
Bot has two main parts:
1. Forget Code 
2. Reservation 

## Setup and Run
```bash
echo 'db.bot_users.createIndex({"user_id": 1}, {unique: true})' | mongo diningbotdb

pip install -r requirements

python main.py
python garbage_collector_main.py
python automatic_reserve_main.py
```
