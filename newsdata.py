import sqlite3

class NewsData:
    def __init__(self, db_name='NewsData.db'):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def create_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS NewsData (
                    id INTEGER PRIMARY KEY,
                    header TEXT,
                    text_ TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_news(self, header, text_):
        try:
            self.cursor.execute("INSERT INTO NewsData (header, text_) VALUES (?, ?)", (header, text_))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding news: {e}")

    def clear_news(self):
        try:
            self.cursor.execute("DELETE FROM NewsData")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error clearing news: {e}")

    def get_news(self):
        try:
            self.cursor.execute("SELECT * FROM NewsData")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting news: {e}")
            return []
