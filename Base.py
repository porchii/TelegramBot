import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.types import ReplyKeyboardRemove
from io import BytesIO
import config as cfg
from database import ScheduleBot
from newsdata import NewsData

bot = Bot(cfg.TOKEN_API)
dp = Dispatcher(bot)
schedule_bot = ScheduleBot()
newsdata_bot = NewsData()

# Обрабрoтка команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет, я Сиа - твой школьный ассистент. Буду рада помочь! 😊\nЧтобы узнать, на что я способна, введи /help')
    sticker_id_or_url = 'CAACAgIAAxkBAAELao9lz0dvx4q1uQJoO2VfTpz1zaeAkAAC8xsAAhSOKUilgjCyi2OkHjQE'
    await bot.send_sticker(message.chat.id, sticker_id_or_url)
    await bot.delete_message(message.chat.id, message.message_id)

# Обрабрoтка команды /help
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("Доступные Вам команды:\n" \
                    "/start - Начать взаимодействие с ботом.\n" \
                    "/help - Получить список доступных команд и их описания.\n" \
                    "/description - Описание бота\n" \
                    "/get_schedule_class [Класс(Формат: 10.2)] - Получить расписание для класса.\n" \
                    "/get_schedule_teacher [Ф.И.О(Формат(Фамилия_И_О))] - Получить расписание для учителя.\n" \
                    "/add_subject [День недели, Время, Предмет(Кабинет), Учитель, Класс]- Добавить урок в расписание.\n" \
                    "/clear - Очистить таблицу\n" \
                    "/get_news - Получить список свежих новостей.\n" \
                    "/add_news [заголовок] [текст] - Добавить новость.\n" \
                    "/clear_news - Очистить список новостей." )
    sticker_id_or_url = 'CAACAgIAAxkBAAELapFlz0me8Z3v44_r3aq8mtn-xxROrgAChR8AAnF-KEiBJKRW6XpGSzQE'
    await bot.send_sticker(message.chat.id, sticker_id_or_url)
    await bot.delete_message(message.chat.id, message.message_id)

# Описание бота
@dp.message_handler(commands=['description'])
async def description(message: types.Message):
    await message.answer("Привет! Я - Сиа, твой надежный школьный компаньон и ассистент. 🤖\n\n" \
        "Функции:\n" \
        "1. **Расписание:** Я могу отправить тебе расписание на нужный день, чтобы ты всегда был в курсе своих занятий.\n"
        "2. **Напоминания о мероприятиях:** Ты больше не упустишь ни одно важное мероприятие! Я буду регулярно информировать тебя о предстоящих уроках и событиях в школе.\n\n" \
        "Просто используй команды, чтобы узнать расписание для класса, учителя, а также добавить новый урок или очистить расписание (доступно только администраторам).\n\n" \
        "Для полного списка команд введи /help. Наслаждайся учебным процессом с Сиа! 😊")
    sticker_id_or_url = 'CAACAgIAAxkBAAELapRlz0nVHFUTvuAnEsGPFNGbuBTyngACdx8AAm-fIEiZSyIJxulbdjQE'
    await bot.send_sticker(message.chat.id, sticker_id_or_url)
    await bot.delete_message(message.chat.id, message.message_id)

# Обработка команды /get_schedule_class
@dp.message_handler(commands=['get_schedule_class'])
async def get_schedule_class(message: types.Message):
    try:
        # Получение аргумента команды
        class_name = message.get_args()

        # Получение расписания для класса
        class_schedule = schedule_bot.get_schedule('class', class_name)

        if not class_schedule:
            await message.reply(f"Расписание для класса {class_name} не найдено. 😢")
            sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
            await bot.send_sticker(message.chat.id, sticker_id_or_url)
            await bot.delete_message(message.chat.id, message.message_id)
            return

        # Форматирование расписания для отправки в чат
        formatted_schedule = "\n".join([f"{row[2]}: {row[3]} с {row[4]}" for row in class_schedule])

        await message.answer(f"Расписание для класса {class_name}:\n{formatted_schedule}", parse_mode=ParseMode.MARKDOWN)
        sticker_id_or_url = 'CAACAgIAAxkBAAELapllz0oyhLzH7Xe3v-QV1wa2EGe_1wACDiIAAu2aIUh7q0_cAVgmTjQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
        sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)

# Обработка команды /get_schedule_teacher
@dp.message_handler(commands=['get_schedule_teacher'])
async def get_schedule_class(message: types.Message):
    try:
        # Получение аргумента команды
        name = message.get_args()

        # Получение расписания для класса
        class_schedule = schedule_bot.get_schedule('teacher', name)

        if not class_schedule:
            await message.reply(f"Расписание для учителя {name} не найдено. 😢")
            sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
            await bot.send_sticker(message.chat.id, sticker_id_or_url)
            await bot.delete_message(message.chat.id, message.message_id)
            return

        # Форматирование расписания для отправки в чат
        formatted_schedule = "\n".join([f"{row[2]}: {row[3]} с {row[5]}" for row in class_schedule])

        await message.answer(f"Расписание для учителя {name}:\n{formatted_schedule}", parse_mode=ParseMode.MARKDOWN)
        sticker_id_or_url = 'CAACAgIAAxkBAAELapllz0oyhLzH7Xe3v-QV1wa2EGe_1wACDiIAAu2aIUh7q0_cAVgmTjQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
        sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)

# Обработка команды /add_subject
@dp.message_handler(commands=['add_subject'])
async def add_subject(message: types.Message):
    if message.from_user.id in cfg.admins:
        try:
            # Получение аргументов команды
            args = message.get_args().split(', ')
            if len(args) != 5:
                raise ValueError("Некорректное количество аргументов. Используйте формат: День, Время, Предмет(Кабинет), Учитель, Класс")
                sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
                await bot.send_sticker(message.chat.id, sticker_id_or_url)

            # Разбор аргументов
            day, time, subject, teacher, class_name = args

            # Добавление урока
            schedule_bot.add_subject(day, time, subject, teacher, class_name)

            await message.reply(f"Урок успешно добавлен в расписание. 👍")
            sticker_id_or_url = 'CAACAgIAAxkBAAELaqFlz0uwJpYufw-JYezwOdyqu_vruwACuhcAAp2oKUixWf4JiHIfqjQE'
            await bot.send_sticker(message.chat.id, sticker_id_or_url)

        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}")
            sticker_id_or_url = 'CAACAgIAAxkBAAELaptlz0ppZknK8J9E1b6dt8-7rb41GwACISQAAofCIUi_1SPKkGeBgzQE'
            await bot.send_sticker(message.chat.id, sticker_id_or_url)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠")
        sticker_id_or_url = 'CAACAgIAAxkBAAELauxlz36UQxASaeyvAZqbsciQ0ial6AACcRkAAgWnIUjo702U0qSNDTQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)
        await bot.delete_message(message.from_user.id, message.message_id)

# Обработка команды /clear
@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    if message.from_user.id in cfg.admins:
        schedule_bot.restore_schedule()
        await message.answer('Расписание очищено и готово к заполнению! 🗑️')
        sticker_id_or_url = 'CAACAgIAAxkBAAELaqFlz0uwJpYufw-JYezwOdyqu_vruwACuhcAAp2oKUixWf4JiHIfqjQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)
        await bot.delete_message(message.from_user.id, message.message_id)
    else:
        await message.answer("У тебя нет прав на выполнение этой команды. 😠")
        sticker_id_or_url = 'CAACAgIAAxkBAAELauxlz36UQxASaeyvAZqbsciQ0ial6AACcRkAAgWnIUjo702U0qSNDTQE'
        await bot.send_sticker(message.chat.id, sticker_id_or_url)
        await bot.delete_message(message.from_user.id, message.message_id)

# Обработка команды /get_news
@dp.message_handler(commands=['get_news'])
async def get_news(message: types.Message):
    news = newsdata_bot.get_news()
    if not news:
        await message.answer("Новостей пока что нет. 😢")
        await bot.delete_message(message.chat.id, message.message_id)
        return
    else:
        formatted_news = "\n".join([f"{row[1]}\n\n {row[2]}" for row in news])
        await message.answer(f"Вот список свежих новостей: \n\n {formatted_news}", parse_mode=ParseMode.MARKDOWN)
        await bot.delete_message(message.chat.id, message.message_id)

# Обработка команды /add_news
@dp.message_handler(commands=['add_news'])
async def add_news_command(message: types.Message):
    # Проверяем, является ли пользователь администратором
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠")
        await bot.delete_message(message.chat.id, message.message_id)
        return

    # Получаем аргументы команды
    args = message.get_args().split(' ', 1)
    
    if len(args) != 2:
        await message.answer("Некорректное количество аргументов. Используйте формат: /add_news [заголовок] [текст]")
        await bot.delete_message(message.chat.id, message.message_id)
        return

    header, text_ = args

    # Добавляем новость
    newsdata_bot.add_news(header, text_)
    
    await message.answer(f"Новость успешно добавлена: \n\nЗаголовок: {header}\nТекст: {text_} 😊")
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELa-ll0HHe-RyvH7qud0DofNiYa_7kkgACuhcAAp2oKUixWf4JiHIfqjQE')
    await bot.delete_message(message.chat.id, message.message_id)

# Обработка команды /clear_news
@dp.message_handler(commands='clear_news')
async def clear_news(message: types.Message):
    if message.from_user.id not in cfg.admins:
        await message.answer("У Вас нет прав на выполнение этой команды. 😠")
        await bot.delete_message(message.chat.id, message.message_id)
        return
    else:
        newsdata_bot.clear_news()
        await message.answer('Новости очищены! 🗑️');
        await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELa-ll0HHe-RyvH7qud0DofNiYa_7kkgACuhcAAp2oKUixWf4JiHIfqjQE')
        await bot.delete_message(message.chat.id, message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
