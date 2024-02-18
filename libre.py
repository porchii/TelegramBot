import pyexcel_ods3
from Base import schedule_bot

# Открываем файл ODS
book_data = pyexcel_ods3.get_data("schedulee.ods")
sheet = book_data['Sheet1']
for row in sheet:
    # Проверяем, что у нас достаточно значений в строке
    if len(row) >= 5:
        day, time, subject, teacher, class_name = row
        schedule_bot.add_subject(day, time, subject, teacher, class_name)
