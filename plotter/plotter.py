
import sqlite3
from relay.utils import *
from pathlib import Path
from datetime import datetime,timedelta

class Plotter:

    time_deltas = {'minute':timedelta(minutes=1),
                   'hour':timedelta(hours=1),
                   'day':timedelta(days=1),
                   'month':timedelta(days=30),
                   'year':timedelta(days=365)}

    def __init__(self, control):
        self.control = control
        self.db = None
        self.table_name = Configured.db_table_name

    def connect(self):
        if not self.db:
            Info('Plotter connects to database')
            db_uri = f'file:///{Configured.database}'
            print(db_uri)
            if Configured.database.exists():
                try:
                    self.db = sqlite3.connect(f'{db_uri}?mode=ro', uri=True)
                except IOError as e:
                    print(f'ERROR: Can not connect to db {log}\n\n')
                    print(e)
                    self.db = None
            else:
                Warning(f'Could not read db file {db_uri}')

    def quit(self):
        if self.db:
            Info('Plotter disconnects from database')
            self.db.close()

    def get_time_range(self,dt='day', end_time=datetime.now()):
        seconds = self.time_ranges[dt]
        start_time = end_time - self.time_deltas[dt]
        return (start_time, end_time)

    def get_data(self,dt,columns):
        self.connect()
        list_fill = ', '.join(columns)
        sql = f'''SELECT time, {list_fill} FROM "{self.table_name}";'''
        print(sql)
        cursor = self.db.execute(sql)
        return cursor.fetchall()

