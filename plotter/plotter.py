
import sqlite3
from relay.utils import *
from pathlib import Path
from datetime import datetime,timedelta
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from numpy import array

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
        self.columns = None

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

    def get_data(self, dt, time_range=None):
        self.connect()
        list_fill = ', '.join(self.columns)
        sql = f'''SELECT time, {list_fill} FROM "{self.table_name}";'''
        print(sql)
        cursor = self.db.execute(sql)
        return array(cursor.fetchall())

    def simple_plot(self, data):
        data = data.transpose()
        fig, axis = plt.subplots(figsize=(12.96,8), facecolor='#454545')
        axis.set_facecolor('#454545')
        axis.tick_params(labelcolor='tab:orange')
        axis.plot(data[0], data[1], label=self.columns[0])
        axis.plot(data[0], data[2], label=self.columns[1])
        axis.grid(True, color='#353535')
        axis.legend()
        fig_url = '/static/images/plot.png'
        plt.savefig('flaskr'+fig_url)
        return fig_url



