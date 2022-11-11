import asyncio
import sqlite3
import wikipedia
import requests

from bs4 import BeautifulSoup

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import random
import Database

TOKEN = "5675697408:AAGvQfcLXRLr1Rvcu_y6Qyv4bqrR9LPenbY"

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)

global db
db = Database.Database()

db.createTable()

d = dict()
base = sqlite3.connect("answers.db")
cur = base.cursor()
base.execute('CREATE TABLE IF NOT EXISTS {}(key text, reply text)'.format('data'))
cur.execute('select key, reply from data')
result = cur.fetchall()
for key, reply in result:
    d[key] = reply
print("ok")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")


@dp.message_handler(commands=['rnd'])
async def process_help_command(message: types.Message):
    await message.reply(f"Рандомное число от 1 до 1000: {random.randint(1, 1000)}")


@dp.message_handler(commands=['addcity'])
async def city_command(msg: types.Message):
    db.addindb(msg.text[9:])
    # await msg.reply(msg.text)
    # await bot.send_message(msg.from_user.id, msg.text)@dp.message_handler(commands=['getcity'])


async def get_city(msg: types.Message):
    language = "ru"
    wikipedia.set_lang(language)
    wikipage = wikipedia.page(msg.text[9:])
    summary = wikipage.summary
    summary = summary[:1000]
    link = db.getcityimg(msg.text[9:])
    for i in range(999, 1, -1):
        if summary[i] == ".":
            summary = summary[:i]
            break
    await bot.send_photo(msg.chat.id, link, caption=summary)


@dp.message_handler(commands=['wiki', 'вики'])
async def wiki(msg: types.Message):
    language = "ru"
    wikipedia.set_lang(language)
    wikipage = wikipedia.page(msg.text[5:])
    summary = wikipage.summary
    if len(summary) > 1000:
        summary = summary[:1000]
        for i in range(999, 1, -1):
            if summary[i] == ".":
                summary = summary[:i]
                break
        if len(wikipage.images) != 0:
            image = wikipage.images[0]
            for i in range(len(wikipage.images)):
                img = wikipage.images[i]
                if img[-4:] != '.svg' and img[-4:] != '.JPG':
                    image = wikipage.images[i]
                    break
            if image[-4:] == '.svg' and image[-4:] == '.JPG':
                image = 'https://cdn-icons-png.flaticon.com/512/2748/2748558.png'
        else:
            image = 'https://cdn-icons-png.flaticon.com/512/2748/2748558.png'
        await bot.send_photo(msg.chat.id, image, caption=summary)


@dp.message_handler(commands=["cities"])
async def play_cities(msg: types.Message):
    message = msg.text[7:]
    citybase = sqlite3.connect('city.db')
    curcity = citybase.cursor()
    curcity.execute("SELECT path FROM game WHERE tgid = ?", (msg.chat.id,))
    data = curcity.fetchall()
    if len(data) == 0:
        curcity.execute('INSERT INTO game(tgid, path, move) VALUES (?, ?, ?)', (msg.chat.id, "", 0))
        base.commit()
    else:
        pass

    a = db.getlastcity(msg.chat.id)
    move = db.returnmove(msg.chat.id)
    if move == 0:
        b = message
    else:
        b = db.rndcity(msg.chat.id, a[len(a) - 1])
    if b != "$sudo -":
        if a[len(a) - 1] == 'ь':
            if a[len(a) - 2] == b[0]:
                print("ВЕРНО")
                db.setcityindb(msg.chat.id, message)
            else:
                print("НЕВЕРНО")
        else:
            if a[len(a) - 1] == b[0]:
                print("ВЕРНО")
                db.setcityindb(msg.chat.id, message)
            else:
                print("НЕВЕРНО")
    else:
        await bot.send_message(msg.from_user.id, "Город не найден в бд")


@dp.message_handler()
async def answers(msg: types.Message):
    message = msg.text
    if message.lower() == "привет":
        await bot.send_message(msg.chat.id, 'хай')
    elif message.lower() == "пока":
        await bot.send_message(msg.chat.id, "Пока((")
    elif message[0] == "?":
        answer = message[1:].split("->")
        d[f'{answer[0]}'] = answer[1]
        cur.execute('INSERT INTO data VALUES (?, ?)', (answer[0].lower(), answer[1]))
        base.commit()
        await bot.send_message(msg.chat.id, "Значения добавлены в словарь")
    elif message.lower() in d:
        await bot.send_message(msg.chat.id, d[message.lower()])
    else:
        await bot.send_message(msg.chat.id, "Не поняла вашего ответа...")


if __name__ == '__main__':
    executor.start_polling(dp)
