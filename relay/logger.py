#!/usr/bin/env python3
import sys
import sqlite3
from relay.utils import *

from datetime import datetime

class DbLogger:
    time_fmt = '%Y%m%d_%H.%M.%S'

    @staticmethod
    def data_type_name(value):
        if isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'FLOAT'
        elif isinstance(value, str):
            return 'TEXT'

    def __init__(self, log, actors):
        self.table_name = Configured.db_table_name
        self.interval = 60 
        self.last_dump = datetime.now()
        self.actors = actors
        self.sql_queue = []
        try:
            # FIXME where and how to close this?
            self.db = sqlite3.connect(log)
        except IOError as e:
            print(f'ERROR: Can not connect to db {log}\n\n')
            print(e)
            self.db = None

        self.column_names = ['time']
        self.column_types = ['INTEGER']
        for actor in self.actors:
            self.column_names += actor.log_data().keys()
            self.column_types += \
                    [self.data_type_name(v) for v in actor.log_data().values()]

        if not self.has_table(self.table_name):
            self.create_table(self.table_name)

    def has_table(self, name):
        cursor = self.db.cursor()
        sql = f'''SELECT name FROM sqlite_master WHERE type="table" AND name="{name}";'''
        cursor.execute(sql)
        return cursor.fetchone()

    def create_table(self, name):
        print(f'Creating log table {name}')
        col_defs = []
        for item in zip(self.column_names, self.column_types):
            col_defs.append(' '.join(item))
        cols_str = ', '.join(col_defs)

        sql = f'''CREATE TABLE {self.table_name} 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols_str});'''
        self.db.execute(sql)

    def add_row(self, row_values):
        n_cols = len(self.column_names)
        if not len(row_values) == n_cols:
            print('Inconsistent row value length')
            return
        vals = ','.join(['?']*n_cols)
        names = ','.join(self.column_names)
        sql = f'''INSERT INTO {self.table_name} ({names}) VALUES({vals});'''
        self.db.cursor().execute(sql, row_values)

    def update(self):
        now = datetime.now()
        row = []
        if (now - self.last_dump).total_seconds() > self.interval:
            row = [int(now.timestamp())]
            for actor in self.actors:
                row += actor.log_data().values()
            self.last_dump = now
        if row:
            try:
                self.add_row(row)
                self.db.commit()
            except:
                print('DATABASE could not add row. Might be locked. FIXME.')

        #c = self.db.execute('SELECT * FROM "history";')
        #Print(c.fetchall())

    def get_last_row(self):
        sql = f'''SELECT * FROM {self.table_name} WHERE   ID =
                  (SELECT MAX(ID)  FROM {self.table_name});'''
        result = self.db.cursor().execute(sql)
        return result.fetchone()

if __name__ == '__main__':
    log = DbLogger('log_db.sql')
    if not log.has_table('history'):
        log.create_table('history')
    log.add_row([1,2,3,4,5,6,7,8,9])
    log.add_row([1,2,3,4,5,6,7,8,10])
    log.db.commit()
    c = log.db.execute('SELECT * FROM "history";')
    print(c.fetchall())


