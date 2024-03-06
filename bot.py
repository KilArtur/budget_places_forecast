import asyncio

import pandas as pd
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from setting import *
from data import *


class GetChance(StatesGroup):
    state_start = State()
    main_menu = State()
    useful_info = State()
    hw_it_work = State()
    get_direction_name = State()
    get_priority = State()
    get_competitive_scores = State()
    get_achievement_scores = State()
    get_ege_objects_number = State()
    get_citizenship = State()
    get_with_ege_status = State()


async def get_prediction_and_probabilities(data):
    df = pd.DataFrame([data])
    numeric_features = loaded_pipeline.numeric_features
    categorical_features = loaded_pipeline.categorical_features
    df_numeric = df[numeric_features]
    df_categorical = df[categorical_features]
    df_processed = pd.concat([df_numeric, df_categorical], axis=1)
    prediction = loaded_pipeline.predict(df_processed)
    probabilities = loaded_pipeline.predict_proba(df_processed)
    probabilities_class_1 = probabilities[:, 1]
    return prediction, probabilities_class_1


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(GetChance.main_menu)
    await message.answer(welcome_text, reply_markup=main_keyboard)


@dp.message(GetChance.main_menu)
async def main_menu(message: types.Message, state: FSMContext):
    if message.text == 'Узнать свои шансы на поступление':
        await state.set_state(GetChance.get_direction_name)
        await message.answer("Введите номер специальности")
    elif message.text == 'Полезная информация':
        await state.set_state(GetChance.useful_info)
        await message.answer("Хорошо, что вам интересно?", reply_markup=useful_keyboard)
    elif message.text == 'Как это работает?':
        await message.answer(hw_it_works_about, reply_markup=main_keyboard)


@dp.message(GetChance.useful_info)
async def main_menu(message: types.Message, state: FSMContext):
    if message.text == 'О ГУАП':
        await message.answer(about_suai)
    elif message.text == 'О военном учебном центре':
        await message.answer(about_guap_army)
    elif message.text == 'Информация о приёмной комисии':
        await message.answer(comission_info)
    elif message.text == 'Учебный процесс':
        await message.answer(about_study_process)
    elif message.text == 'Баллы прошлых лет':
        await message.answer(previous_points)
    elif message.text == 'Назад':
        await state.set_state(GetChance.main_menu)
        await message.answer('Окей, идем в главное меню', reply_markup=main_keyboard)
    else:
        await message.answer('Выберите пункт из перечня')


@dp.message(GetChance.get_direction_name)
async def process_direction_name(message: types.Message, state: FSMContext):
    if message.text in DIRECTIONS:
        await state.update_data(name=message.text)
        await state.set_state(GetChance.get_priority)
        await message.answer("Введите числом, приоритет выбранной специальности")
    else:
        await message.answer('Выбранной специальности либо нет, либо вы ввели её неправильно. Пример 09.03.03')


@dp.message(GetChance.get_priority)
async def process_priority(message: types.Message, state: FSMContext):
    if message.text in PROIRITIES:
        await state.update_data(priority=int(message.text))
        await state.set_state(GetChance.get_with_ege_status)
        await message.answer('Поступаете по баллам ЕГЭ или по вступительным экзаменам?',
                             reply_markup=with_ege_or_not_keyboard)
    else:
        await message.answer('Введите приоритет в формате числа от 1 до 10')


# Обработчик для состояния get_with_ege_status
@dp.message(GetChance.get_with_ege_status)
async def process_with_ege_status(message: types.Message, state: FSMContext):
    # Сохраняем статус по ЕГЭ в контексте состояния
    if message.text == 'Поступаю по баллам ЕГЭ':
        await state.update_data(with_ege=1)
        await message.answer("Введите ваши конкурсные баллы")
        await state.set_state(GetChance.get_competitive_scores)
    elif message.text == 'Поступаю по вступительными экзаменам':
        await state.update_data(with_ege=0)
        await message.answer("Введите ваши конкурсные баллы")
        await state.set_state(GetChance.get_competitive_scores)
    else:
        await message.answer('Выберите из перечня')


# Обработчик для состояния get_competitive_scores
@dp.message(GetChance.get_competitive_scores)
async def process_competitive_scores(message: types.Message, state: FSMContext):
    # Сохраняем конкурсные баллы в контексте состояния
    if message.text.isdigit():
        await state.update_data(competitive_scores=int(message.text))
        # Переходим в следующее состояние
        await state.set_state(GetChance.get_achievement_scores)
        await message.answer("Введите ваши дополнительные баллы за достижения")
    else:
        await message.answer('Введите свои конкурсные баллы корректно')


# Обработчик для состояния get_achievement_scores
@dp.message(GetChance.get_achievement_scores)
async def process_achievement_scores(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        # Сохраняем баллы по достижениям в контексте состояния
        await state.update_data(achievement_scores=int(message.text))
        # Переходим в следующее состояние
        if data['with_ege']:
            await state.set_state(GetChance.get_ege_objects_number)
            await message.answer("Введите количество предметов ЕГЭ, которые вы сдавали")
        else:
            await state.update_data(ege_average_score=0)
            await message.answer("Введите ваше гражданство", reply_markup=countries_keyboard)
            await state.set_state(GetChance.get_citizenship)
    else:
        await message.answer('Введите свои баллы за достижения корректно')


# Обработчик для состояния get_ege_objects_number
@dp.message(GetChance.get_ege_objects_number)
async def process_ege_objects_number(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        ege_average_score = int((data['competitive_scores'] + data['achievement_scores']) / int(message.text))
        await state.update_data(ege_average_score=ege_average_score)
        await state.set_state(GetChance.get_citizenship)
        await message.answer("Выберите ваше гражданство", reply_markup=countries_keyboard)
    else:
        await message.answer('Введите количество предметов корректно')


# Обработчик для состояния get_citizenship
@dp.message(GetChance.get_citizenship)
async def process_citizenship(message: types.Message, state: FSMContext):
    if message.text in COUNTRIES:
        await state.update_data(citizenship=COUNTRIES[message.text])
        data = await state.get_data()
        prediction, probabilities_class_1 = await get_prediction_and_probabilities(data)
        await message.answer('⏳ Секундочку, производятся вычисления... 🤖🧠✨')
        await asyncio.sleep(3)
        if probabilities_class_1[0] <= 0.4:
            await message.answer(
                f'🤔 Модель машинного обучения не слишком уверена, что вы пройдете на выбранную вами специальность,'
                f' ведь шанс поступления составляет {probabilities_class_1[0] * 100:.2f}%... 📉 '
                f'Настоятельно рекомендуем присмотреться к другим захватывающим направлениям! 🚀🤓 '
                f'(Более подробные данные и баллы прошлых лет доступны здесь https://priem.guap.ru/bach/archive) 📊✨',
                reply_markup=main_keyboard)
            await state.set_state(GetChance.main_menu)

        elif 0.4 < probabilities_class_1[0] <= 0.8:
            await message.answer(
                f'У вас хороший шанс для поступления на выбранную специальность, который составляет'
                f' {probabilities_class_1[0] * 100:.2f}%! 🌟 Но не забывайте, что мир университета богат разнообразием.'
                f'  Советуем вам также приглядеться к другим увлекательным специальностям.'
                f' 🚀📚 (Подробные баллы прошлых лет можно посмотреть здесь https://priem.guap.ru/bach/archive) 📊✨',
                reply_markup=main_keyboard)
            await state.set_state(GetChance.main_menu)

        elif probabilities_class_1[0] > 0.8:
            await message.answer(
                f'🌟 Ничего себе, у вас отличные шансы на поступление выбранной вами специальности!'
                f' Шанс на поступление составляет {probabilities_class_1[0] * 100:.2f}%🚀 '
                f'Ждем вас в нашем прекрасном университете! 🎓✨',
                reply_markup=main_keyboard)
            await state.set_state(GetChance.main_menu)

    else:
        await message.answer('Выберите гражданство страны из перечня', reply_markup=countries_keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
