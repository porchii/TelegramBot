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
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELao9lz0dvx4q1uQJoO2VfTpz1zaeAkAAC8xsAAhSOKUilgjCyi2OkHjQE')
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("<b>Доступные команды:</b>\n" \
                         "/start - Начать взаимодействие с ботом.\n" \
                         "/help - Получить список доступных команд и их описания.\n" \
                         "/description - Описание бота\n" \
                         "/get_schedule_class [Класс(Формат: 10.2)] - Получить расписание для класса.\n" \
                         "/get_schedule_teacher [Ф.И.О(Формат(Фамилия_И_О))] - Получить расписание для учителя.\n" \
                         "/create_new_schedule - Обновление расписания в соответствии с таблицей.\n" \
                         "/clear - Очистить таблицу\n" \
                         "/get_news - Получить список свежих новостей.\n" \
                         "/add_news [заголовок] [текст] - Добавить новость.\n" \
                         "/clear_news - Очистить список новостей.", parse_mode=ParseMode.HTML)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELapFlz0me8Z3v44_r3aq8mtn-xxROrgAChR8AAnF-KEiBJKRW6XpGSzQE')
    await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['description'])
async def description(message: types.Message):
    await message.answer("Привет! Я - Сиа, твой надежный школьный компаньон и ассистент. 🤖\n\n" \
                         "<b>Функции:</b>\n" \
                         "1. <b>Расписание:</b> Я могу отправить тебе расписание на нужный день, чтобы ты всегда был в курсе своих занятий.\n"
                         "2. <b>Напоминания о мероприятиях:</b> Ты больше не упустишь ни одно важное мероприятие! Я буду регулярно информировать тебя о предстоящих уроках и событиях в школе.\n\n" \
                         "Просто используй команды, чтобы узнать расписание для класса, учителя, а также добавить новый урок или очистить расписание (доступно только администраторам).\n\n" \
                         "Для полного списка команд введи /help. Наслаждайся учебным процессом с Сиа! 😊", parse_mode=ParseMode.HTML)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELapRlz0nVHFUTvuAnEsGPFNGbuBTyngACdx8AAm-fIEiZSyIJxulbdjQE')
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


@dp.message_handler(commands=['get_schedule_class'])
async def get_schedule_class(message: types.Message):
    class_name = message.get_args()
    await get_schedule(message, 'class', class_name)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELeeFl2Hpvjs_Jept9orjqQrh4LzMAAXcAAvMbAAIUjilIpYIwsotjpB40BA')

@dp.message_handler(commands=['get_schedule_teacher'])
async def get_schedule_teacher(message: types.Message):
    teacher_name = message.get_args()
    await get_schedule(message, 'teacher', teacher_name)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELeeFl2Hpvjs_Jept9orjqQrh4LzMAAXcAAvMbAAIUjilIpYIwsotjpB40BA')

@dp.message_handler(commands=['create_new_schedule'])
async def create_new_schedule_command(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.create_new_schedule()
        await message.reply('Новое расписание успешно создано! 🗓️', parse_mode=ParseMode.HTML)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELbgABZdHVHLXsLu4XygYGXzGNXCdLEmsAAl4bAAL5yWFI-Stggz85tSI0BA')
        await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.restore_schedule()
        await message.answer('Расписание очищено и готово к заполнению! 🗑️', parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELaqFlz0uwJpYufw-JYezwOdyqu_vruwACuhcAAp2oKUixWf4JiHIfqjQE')
        await bot.delete_message(message.from_user.id, message.message_id)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELbgABZdHVHLXsLu4XygYGXzGNXCdLEmsAAl4bAAL5yWFI-Stggz85tSI0BA')
        await bot.delete_message(message.from_user.id, message.message_id)

@dp.message_handler(commands=['get_news'])
async def get_news(message: types.Message):
    news = newsdata_bot.get_news()
    if not news:
        await message.answer("Новостей пока что нет. 😢", parse_mode=ParseMode.HTML)
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        formatted_news = "\n".join([f"{row[1]}\n\n {row[2]}" for row in news])
        await message.answer(f"Вот список свежих новостей: \n\n {formatted_news}", parse_mode=ParseMode.HTML)
        await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands=['add_news'])
async def add_news_command(message: types.Message):
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELbgABZdHVHLXsLu4XygYGXzGNXCdLEmsAAl4bAAL5yWFI-Stggz85tSI0BA')
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        args = message.get_args().split(' ', 1)
        if len(args) != 2:
            await message.answer("Некорректное количество аргументов. Используйте формат: /add_news [заголовок] [текст]", parse_mode=ParseMode.HTML)
            await bot.delete_message(message.chat.id, message.message_id)
        else:
            header, text_ = args
            newsdata_bot.add_news(header, text_)
            await message.answer(f"Новость успешно добавлена: \n\nЗаголовок: {header}\nТекст: {text_} 😊", parse_mode=ParseMode.HTML)
            await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELa-ll0HHe-RyvH7qud0DofNiYa_7kkgACuhcAAp2oKUixWf4JiHIfqjQE')
            await bot.delete_message(message.chat.id, message.message_id)

@dp.message_handler(commands='clear_news')
async def clear_news(message: types.Message):
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠", parse_mode=ParseMode.HTML)
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELbgABZdHVHLXsLu4XygYGXzGNXCdLEmsAAl4bAAL5yWFI-Stggz85tSI0BA')
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        newsdata_bot.clear_news()
        await message.answer('Новости очищены! 🗑️', parse_mode=ParseMode.HTML);
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELa-ll0HHe-RyvH7qud0DofNiYa_7kkgACuhcAAp2oKUixWf4JiHIfqjQE')
        await bot.delete_message(message.chat.id, message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
