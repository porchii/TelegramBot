import sqlite3
import telegram
import aioschedule
import threading
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode, ReplyKeyboardRemove
from aiogram.types import InputFile
from io import BytesIO
import config as cfg
from tabulate import tabulate
from database import ScheduleBot
from teachers_ import Teachers
import asyncio
from datetime import datetime
import time
import pyexcel_ods3
from newsdata import NewsData
import functools

bot = Bot(cfg.TOKEN_API)
dp = Dispatcher(bot)
schedule_bot = ScheduleBot()
newsdata_bot = NewsData()
teacher_subjects = Teachers()

async def good_morning():
    for class_name in cfg.class_chats:
        await bot.send_message(cfg.class_chats[class_name], 'Доброе утро! 📚✨ Пусть этот день будет насыщенным знаниями и успешными открытиями! 💪🌅 Удачи в учебе! 🚀')

async def on_startup(dp):
    print("Да!")

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет, я Сиа - твой школьный ассистент. Буду рада помочь! 😊\nЧтобы узнать, на что я способна, введи /help')
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmI1l4zjANitXFQ3WYCD6lAWfCHCzGwACAicAAk6MIEryF51-qbPiLTQE')
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("<b>Доступные команды:</b>\n" \
                         "<b>/start</b> - <i>Начать взаимодействие с ботом.</i>\n" \
                         "<b>/help</b> - <i>Получить список доступных команд и их описания.</i>\n" \
                         "<b>/description</b> - <i>Описание бота</i>\n" \
                         "<b>/class</b> [Класс(Формат: 10.2)] - <i>Получить расписание для класса.</i>\n" \
                         "<b>/teacher</b> [Ф.И.О(Формат(Фамилия_И_О))] - <i>Получить расписание для учителя.</i>\n" \
                         "<b>/update</b> - <i>Обновление расписания в соответствии с таблицей.</i>\n" \
                         "<b>/clear</b> - <i>Очистить таблицу</i>\n" \
                         "<b>/news</b> - <i>Получить список свежих новостей.</i>\n" \
                         "<b>/add_news</b> [заголовок] [текст] - <i>Добавить новость.</i>\n" \
                         "<b>/clear_news</b> - <i>Очистить список новостей.</i>\n" \
                         "<b>/photo</b> - <i>Отправить фото в каналы с расписанием.</i>\n", parse_mode=ParseMode.HTML)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmI9l4zkafaYNlBuzqJDvRB2ahn-P-QACMiYAAn8ZKEpL8r0dbah9sTQE')
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['description'])
async def description(message: types.Message):
    await message.answer("Привет! Я - Сиа, твой надежный школьный компаньон и ассистент. 🤖\n\n" \
                         "<b>Функции:</b>\n" \
                         "1. <b>Расписание:</b> Я могу отправить тебе расписание на нужный день, чтобы ты всегда был в курсе своих занятий.\n"
                         "2. <b>Напоминания о мероприятиях:</b> Ты больше не упустишь ни одно важное мероприятие! Я буду регулярно информировать тебя о предстоящих уроках и событиях в школе.\n\n" \
                         "Просто используй команды, чтобы узнать расписание для класса, учителя, а также добавить новый урок или очистить расписание (доступно только администраторам).\n\n" \
                         "Для полного списка команд введи /help. Наслаждайся учебным процессом с Сиа! 😊", parse_mode=ParseMode.HTML)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJFl4zkwa-GjAelL8GZweMNyITR2uAACXiQAAvB-KUoRWB6wYUjbSTQE')
    await bot.delete_message(message.chat.id, message.message_id)

async def get_schedule(message: types.Message, class_type: str, class_name: str):
    try:
        if not class_name:
            await message.answer("Не указан класс или учитель.", parse_mode=ParseMode.HTML)
            return

        class_schedule = schedule_bot.get_schedule(class_type, class_name)

        if not class_schedule:
            await message.answer(f"Расписание для {class_name} не найдено. 😢", parse_mode=ParseMode.HTML)
            return
        table_data = []
        current = 0
        if (class_type == 'teacher'):
            for i in range(0, len(class_schedule)):
                if (i == 0 or class_schedule[i - 1][2] != class_schedule[i][2]):
                    current += 1
                table_data.append((current, f'{class_schedule[i][1]}-{class_schedule[i][2]}', class_schedule[i][3], class_schedule[i][5]))
            table = tabulate(table_data, headers=["№", "Время", "Предмет", "Класс"], tablefmt="presto")


        if (class_type == 'class'):
            for i in range(0, len(class_schedule)):
                if (i == 0 or class_schedule[i - 1][2] != class_schedule[i][2]):
                    current += 1
                table_data.append((current, f'{class_schedule[i][1]}-{class_schedule[i][2]}', class_schedule[i][3]))
            table = tabulate(table_data, headers=["№", "Время", "Предмет"], tablefmt="presto")

        code_block = f"```\n{table}\n```"
        return code_block


    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['class'])
async def get_schedule_class(message: types.Message):
    class_name = message.get_args()
    table = await get_schedule(message, 'class', class_name)
    await bot.send_message(message.chat.id, table, parse_mode=ParseMode.MARKDOWN)
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['teacher'])
async def get_schedule_teacher(message: types.Message):
    teacher_name = message.get_args()
    table = await get_schedule(message, 'teacher', teacher_name)
    await bot.send_message(message.chat.id, table, parse_mode=ParseMode.MARKDOWN)
    await bot.delete_message(message.chat.id, message.message_id)

async def reminde(subject, time_b, time_e, class_name):
    await bot.send_message(cfg.class_chats[class_name], f'Следующий урок {subject} начинается в {time_e}')

async def create_new_schedule():
    rows = schedule_bot.get_table()
    send_good_morning = functools.partial(
        good_morning
    )
    aioschedule.every().day.at('07:00').do(send_good_morning)
    for i in range(len(rows) - 1):
        if rows[i + 1][5] == rows[i][5]:
            reminder_partial = functools.partial(
                reminde,
                subject=rows[i + 1][3],
                time_b=rows[i][2],
                time_e=rows[i + 1][1],
                class_name=rows[i][5]
            )
            aioschedule.every().day.at(rows[i][2]).do(reminder_partial)
    
async def print_all_jobs():
    print("All jobs:")
    for job in aioschedule.jobs:
        print(job)

@dp.message_handler(commands=['update'])
async def update(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.update()
        aioschedule.clear()
        await create_new_schedule()
        await print_all_jobs()
        await message.reply('Новое расписание успешно создано! 🗓️', parse_mode=ParseMode.HTML)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJNl4zlg8dOwXM90YWxGA5IgbjhiYAACHyEAAld_KEosM1AOHIFh3jQE')
        await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.restore_schedule()
        aioschedule.clear()
        await message.answer('Расписание очищено и готово к заполнению! 🗑️', parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJVl4zn1Sv9hUyEo8QLGGkB6_Jq9mwACZSYAAmgMKEpujN9gfJg6njQE')
        await bot.delete_message(message.from_user.id, message.message_id)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJNl5zlg8dOwXM90YWxGA5IgbjhiYAACHyEAAld_KEosM1AOHIFh3jQE')
        await bot.delete_message(message.from_user.id, message.message_id)

@dp.message_handler(commands=['news'])
async def get_news(message: types.Message):
    news = newsdata_bot.get_news()
    if not news:
        await message.answer("Новостей пока что нет. 😢", parse_mode=ParseMode.HTML)
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        formatted_news = "\n".join([f"{row[2]}\n\n {row[2]}" for row in news])
        await message.answer(f"Вот список свежих новостей: \n\n {formatted_news}", parse_mode=ParseMode.HTML)
        await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['add_news'])
async def add_news_command(message: types.Message):
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJNl5zlg8dOwXM90YWxGA5IgbjhiYAACHyEAAld_KEosM1AOHIFh3jQE')
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        args = message.get_args().split(' ', 2)
        if len(args) != 3:
            await message.answer("Некорректное количество аргументов. Используйте формат: /add_news [заголовок] [текст]", parse_mode=ParseMode.HTML)
            await bot.delete_message(message.chat.id, message.message_id)
        else:
            header, text_ = args
            newsdata_bot.add_news(header, text_)
            await message.answer(f"Новость успешно добавлена: \n\nЗаголовок: {header}\nТекст: {text_} 😊", parse_mode=ParseMode.HTML)
            await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJVl4zn1Sv9hUyEo8QLGGkB6_Jq9mwACZSYAAmgMKEpujN9gfJg6njQE')
            await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['clear_news'])
async def clear_news(message: types.Message):
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJNl4zlg8dOwXM90YWxGA5IgbjhiYAACHyEAAld_KEosM1AOHIFh3jQE')
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        newsdata_bot.clear_news()
        await message.answer('Новости очищены! 🗑️', parse_mode=ParseMode.HTML);
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJVl4zn1Sv9hUyEo8QLGGkB6_Jq9mwACZSYAAmgMKEpujN9gfJg6njQE')
        await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['run'])
async def run_command(message: types.Message):
    for class_name in cfg.class_chats:
        await bot.send_message(cfg.class_chats[class_name], await get_schedule(message, 'class', class_name), parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(content_types=['photo'])
async def photo_command(message: types.Message):   
    if message.get_command():
        if message.from_user.id not in cfg.admins:
            await message.answer("У Вас нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        else:
            photo = message.photo[-1]
            for class_chat_id in [cfg.class_chats['10.1'], cfg.class_chats['10.2']]:
                await bot.send_photo(chat_id=class_chat_id, photo=photo.file_id)
            await message.answer("Фото успешно отправлено в чаты 10.1 и 10.2 классов.")

loop = asyncio.get_event_loop()

async def scheduled_job():
    while True:
        await asyncio.sleep(1)
        await aioschedule.run_pending()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(create_new_schedule()) 
    loop.create_task(scheduled_job())
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    loop.run_forever()