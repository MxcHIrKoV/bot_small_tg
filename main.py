from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from environs import Env

import sqlite3

env = Env()
env.read_env()
bot_token = env('BOT_TOKEN')

bot = Bot(token=bot_token)
dp = Dispatcher()

conn = sqlite3.connect('stat.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER,
    username TEXT,
    num_msg INTEGER
     )""")
conn.commit()


def check_db(user_id):
    cur.execute("""SELECT user_id FROM users""")
    id_user = cur.fetchall()

    conn.commit()
    # print(user_id)

    for i in id_user:
        if user_id in i:
            return True


def up_num_msg(user_id):
    cur.execute(f"""SELECT num_msg FROM users WHERE user_id={user_id}""")
    num = cur.fetchall()  # [(0,)]
    num = num[0][0]
    num += 1

    cur.execute(f"""UPDATE users SET num_msg={num} WHERE user_id={user_id}""", )
    conn.commit()


@dp.message(CommandStart())
async def start(message: Message):
    # info = message.chat.title
    await message.answer("Вроде работает")


@dp.message(Command(commands="save_db"))
async def save_bd(message: Message):
    user_id = message.from_user.id
    if not check_db(user_id):

        cur.execute("""INSERT INTO users (user_id, username, num_msg) VALUES (?, ?, ?)""",
                    (message.from_user.id, message.from_user.username, 0))
        conn.commit()
        await message.reply("Ты сохранен в базе")

    else:

        await message.reply("Ты уже есть в бд")


@dp.message(Command(commands="statistics"))
async def statistics(message: Message):
    cur.execute("""SELECT * FROM users""")
    ctx = cur.fetchall()
    conn.commit()
    # print(ctx)
    text = ""

    for _ in ctx:
        t = f"@{_[1]} - {_[2]}\n"
        text += t

    # print(text)
    await message.answer(text)


@dp.message()
async def msg(message: Message):
    user_id = message.from_user.id
    check = check_db(user_id)

    if check:
        up_num_msg(user_id)


if __name__ == '__main__':
    dp.run_polling(bot)
