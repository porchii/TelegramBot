import pyexcel_ods3
from Base import schedule_bot
from Base import teacher_subjects

book_data = pyexcel_ods3.get_data("schedulee.ods")
sheet = book_data['Sheet1']

for i in range(1, len(sheet)):
    for j in range(2, len(sheet[i])):
        try:
            
            teacher = teacher_subjects.get_teacher_by_subject_and_class(sheet[i][j].split('(')[0], sheet[0][j])
            if sheet[i][j]:
                schedule_bot.add_subject('x', sheet[i][1], sheet[i][j], teacher, sheet[0][j])
                print(f'Успешно добавлен урок в строке {i + 1}, столбце {j + 1}')
                
        except Exception as e:
            print(f'Ошибка в строке {i + 1}, столбце {j + 1}: {e}')
