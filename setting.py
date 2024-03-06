import joblib as joblib
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN

form_router = Router()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


main_keyboard = [
    [types.KeyboardButton(text='Узнать свои шансы на поступление')],
    [types.KeyboardButton(text='Как это работает?')],
    [types.KeyboardButton(text='Полезная информация')],

]
main_keyboard = types.ReplyKeyboardMarkup(keyboard=main_keyboard, one_time_keyboard=True, resize_keyboard=True)

useful_keyboard = [
    [types.KeyboardButton(text='О ГУАП')],
    [types.KeyboardButton(text='О военном учебном центре')],
    [types.KeyboardButton(text='Информация о приёмной комисии')],
    [types.KeyboardButton(text='Учебный процесс')],
    [types.KeyboardButton(text='Баллы прошлых лет')],
    [types.KeyboardButton(text='Назад')],

]
useful_keyboard = types.ReplyKeyboardMarkup(keyboard=useful_keyboard, resize_keyboard=True)

with_ege_or_not_keyboard = [
    [types.KeyboardButton(text='Поступаю по баллам ЕГЭ')],
    [types.KeyboardButton(text='Поступаю по вступительными экзаменам')],
]
with_ege_or_not_keyboard = types.ReplyKeyboardMarkup(keyboard=with_ege_or_not_keyboard, one_time_keyboard=True, resize_keyboard=True)

countries_keyboard = [
    [types.KeyboardButton(text='Российская Федерация ')],
    [types.KeyboardButton(text='Беларусь')],
    [types.KeyboardButton(text='Казахстан')],
    [types.KeyboardButton(text='Украина')],
    [types.KeyboardButton(text='Узбекистан')],
    [types.KeyboardButton(text='Армения')],
]

countries_keyboard = types.ReplyKeyboardMarkup(keyboard=countries_keyboard, resize_keyboard=True)

loaded_pipeline = joblib.load('cat_boost_pipeline.joblib')
