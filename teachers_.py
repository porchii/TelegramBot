import sqlite3

class Teachers:
    def __init__(self, db_name='Teachers.db'):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def create_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Teachers (
                    id INTEGER PRIMARY KEY,
                    teacher TEXT,
                    subject TEXT,
                    class_name TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def get_teacher_by_subject_and_class(self, subject, class_name):
        try:
            self.cursor.execute('SELECT teacher FROM Teachers WHERE subject=? AND class_name=?', (subject, class_name))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")