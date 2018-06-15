import sqlite3
import time


class SQLiteLogger:
    def __init__(self, filename="g2x.db"):
        self.filename = filename
        self.connection = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        try:
            with open(self.filename):
                self.connection = sqlite3.connect(self.filename)
        except IOError:
            self.connection = sqlite3.connect(self.filename)
            cursor = self.connection.cursor()
            cursor.execute('''CREATE TABLE readings
                              (date real, device text, property text, value real)''')
            self.connection.commit()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def log(self, device, property, value, t=None):
        if self.connection is not None:
            if t is None:
                t = time.time()
            values = (t, device, property, value)

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO readings VALUES(?,?,?,?)", values)
            self.connection.commit()
