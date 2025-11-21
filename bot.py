import asyncio
import logging
import requests
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = '8513030459:AAGiX1WTsgHxTpQBrfL3o2W3Dqr6Ujs94AI'
VAQT = 300

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def db_start():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users
  
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if add_user(message.from_user.id):
        await message.answer(f"Salom, {message.from_user.first_name}! Siz tilla narxlari kuzatuviga qo'shildingiz.")
    else:
        await message.answer("Siz allaqachon ro'yxatdasiz! ✅")

def get_gold_price():
    try:
        url = "https://data-asg.goldprice.org/dbXRates/USD"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        unsiya = data['items'][0]['xauPrice']
        gramm = unsiya / 31.1035
        return unsiya, gramm
    except Exception as e:
        logging.error(f"Narx olishda xato: {e}")
        return None, None

async def send_price_loop():
    await asyncio.sleep(5)
    while True:
        unsiya, gramm = get_gold_price()
        if unsiya:
            hozir = datetime.now().strftime("%d-%m-%Y | %H:%M")
            xabar = (
                f"🌟 **Tilla Narxi Yangilandi**\n"
                f"📅 {hozir}\n\n"
                f"🔸 **1 Unsiya (31.1g):** ${unsiya:,.2f}\n"
                f"🔹 **1 Gramm:** ${gramm:,.2f}\n"
            )
            
            users = get_all_users()
            for user_id in users:
                try:
                    await bot.send_message(chat_id=user_id, text=xabar, parse_mode="Markdown")
                    await asyncio.sleep(0.1) 
                except Exception:
                    
                    pass 
        
        await asyncio.sleep(VAQT)

async def main():
    db_start() 
    await asyncio.gather(dp.start_polling(bot), send_price_loop())

if __name__ == "__main__":
    asyncio.run(main())
      
