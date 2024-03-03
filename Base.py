import sqlite3
import telegram
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, ReplyKeyboardRemove
from io import BytesIO
import config as cfg
from tabulate import tabulate
from database import ScheduleBot
from teachers_ import Teachers
import pyexcel_ods3
from newsdata import NewsData

bot = Bot(cfg.TOKEN_API)
dp = Dispatcher(bot)
schedule_bot = ScheduleBot()
newsdata_bot = NewsData()
teacher_subjects = Teachers()

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
                         "<b>/clear_news</b> - <i>Очистить список новостей.</i>", parse_mode=ParseMode.HTML)
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
                table_data.append((current, class_schedule[i][2], class_schedule[i][3], class_schedule[i][5]))
            table = tabulate(table_data, headers=["№", "Время", "Предмет", "Класс"], tablefmt="pretty")


        if (class_type == 'class'):
            for i in range(0, len(class_schedule)):
                if (i == 0 or class_schedule[i - 1][2] != class_schedule[i][2]):
                    current += 1
                table_data.append((current, class_schedule[i][2], class_schedule[i][3]))
            table = tabulate(table_data, headers=["№", "Время", "Предмет"], tablefmt="pretty")

        code_block = f"```\n{table}\n```"
        await message.answer(f"Расписание для {class_name}:\n{code_block}", parse_mode=ParseMode.MARKDOWN)


    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['class'])
async def get_schedule_class(message: types.Message):
    class_name = message.get_args()
    await get_schedule(message, 'class', class_name)
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['teacher'])
async def get_schedule_teacher(message: types.Message):
    teacher_name = message.get_args()
    await get_schedule(message, 'teacher', teacher_name)
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['update'])
async def create_new_schedule_command(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.create_new_schedule()
        await message.reply('Новое расписание успешно создано! 🗓️', parse_mode=ParseMode.HTML)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELmJNl4zlg8dOwXM90YWxGA5IgbjhiYAACHyEAAld_KEosM1AOHIFh3jQE')
        await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.restore_schedule()
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
