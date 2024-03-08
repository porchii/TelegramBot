import sqlite3
import pyexcel_ods3
import schedule
import re

class ScheduleBot:
    def __init__(self, db_name='schedule.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY,
                time_b TEXT,
                time_e TEXT,
                subject TEXT,
                teacher TEXT,
                class_name TEXT
            )
        ''')
        self.conn.commit()

    def add_subject(self, time_b, time_e, subject, teacher, class_name):
        self.cursor.execute("INSERT INTO schedule (time_b, time_e, subject, teacher, class_name) VALUES (?, ?, ?, ?, ?)",
                            (time_b, time_e, subject, teacher, class_name))
        self.conn.commit()

    def update(self):
        def go():
            from Base import teacher_subjects
            book_data = pyexcel_ods3.get_data("schedulee.ods")
            sheet = book_data['Sheet1']

            for i in range(2, len(sheet)):
                if i % 2 == 0:
                    for j in range(1, len(sheet[i])):
                        try:
                            subjects = sheet[i][j].split('/')
                            for s in subjects:
                                teacher = teacher_subjects.get_teacher_by_subject_and_class(s.split('(')[0], sheet[0][j])
                                if sheet[i][j]:
                                    time = sheet[i - 1][j].split('-')
                                    self.add_subject(time[0], time[1], s, teacher, sheet[0][j])
                        except Exception as e:
                            print(f'Ошибка в строке {i + 1}, столбце {j + 1}: {e}')
                            
        self.restore_schedule()
        go()


    def restore_schedule(self):
        connection = sqlite3.connect("schedule.db")
        cursor = connection.cursor()
        query = "DELETE FROM schedule"
        cursor.execute(query)
        connection.commit()
        connection.close()

    def get_schedule(self, user_type, user_name):
        if user_type == 'class':
            self.cursor.execute("SELECT * FROM schedule WHERE class_name=?", (user_name,))
        elif user_type == 'teacher':
            self.cursor.execute("SELECT * FROM schedule WHERE teacher=?", (user_name,))
        else:
            return []

        rows = self.cursor.fetchall()
        return rows

    def get_table(self):
        self.cursor.execute("SELECT * FROM schedule")
        rows = self.cursor.fetchall()
        def extract_class_and_time(row):
            match = re.search(r'(\d{2}:\d{2})-(\d{2}:\d{2})', row[2])
            time_value = match.group(1) if match else '00:00'
            class_value = row[5]
            return (class_value, time_value)

        sorted_rows = sorted(rows, key=extract_class_and_time)
        return sorted_rows

    def close_connection(self):
        self.conn.close()
