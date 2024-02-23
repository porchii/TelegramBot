import sqlite3

class ScheduleBot:
    def __init__(self, db_name='schedule.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY,
                day TEXT,
                time TEXT,
                subject TEXT,
                teacher TEXT,
                class_name TEXT
            )
        ''')
        self.conn.commit()

    def add_subject(self, day, time, subject, teacher, class_name):
        self.cursor.execute("INSERT INTO schedule (day, time, subject, teacher, class_name) VALUES (?, ?, ?, ?, ?)",
                            (day, time, subject, teacher, class_name))
        self.conn.commit()


    def remove_subject(self, subject_id):
        self.cursor.execute("DELETE FROM schedule WHERE id=?", (subject_id,))
        self.conn.commit()

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

    def close_connection(self):
        self.conn.close()
