
import sqlite3
from relay.utils import *
from pathlib import Path
from datetime import datetime,timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from numpy import array

class Plotter:

    time_deltas = {'minute':timedelta(minutes=1),
                   'hour':timedelta(hours=1),
                   'hours':timedelta(hours=6),
                   'day':timedelta(days=1),
                   'week':timedelta(days=7),
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
        seconds = self.time_deltas[dt]
        start_time = end_time - self.time_deltas[dt]
        print(f'Plot between {start_time} and {end_time}')
        return (start_time, end_time)

    def get_data(self, dt, time_range=None):
        start_time, end_time = self.get_time_range(dt)
        start_time = int(start_time.timestamp())
        self.connect()
        list_fill = ', '.join(self.columns)
        sql = f'''SELECT time, {list_fill} FROM "{self.table_name}" WHERE time >= {start_time};'''
        print(sql)
        cursor = self.db.execute(sql)
        max_points = 500
        rows = cursor.fetchall()
        if len(rows) > 2*max_points:
            n_skip = int(len(rows)/max_points)
            rows = rows[0::n_skip]
        return array(rows)

    def simple_plot(self, data):
        data = data.transpose()
        fig, (ax1, ax2) = plt.subplots(nrows=2, \
                                       figsize=(12.96,8), \
                                       facecolor='#454545', \
                                       constrained_layout=True)
 
        time_span = data[0][-1] - data[0][0]
        if time_span >= 23*3600:
            major_locator = mdates.DayLocator()
            minor_locator = mdates.HourLocator()
            date_format = mdates.DateFormatter("%Y-%m-%d")
        elif time_span >= 2*3600:
            major_locator = mdates.HourLocator()
            minor_locator = None
            date_format = mdates.DateFormatter("%H")
        else:
            major_locator = mdates.HourLocator()
            minor_locator = mdates.MinuteLocator()
            date_format = mdates.DateFormatter("%H:%M")

        ax1.xaxis.set_major_formatter(date_format)
        ax1.xaxis.set_major_locator(major_locator)
        if minor_locator:
            ax1.xaxis.set_minor_locator(minor_locator)
        ax2.xaxis.set_major_formatter(date_format)
        ax2.xaxis.set_major_locator(major_locator)
        if minor_locator:
            ax2.xaxis.set_minor_locator(minor_locator)

        x_time = [datetime.fromtimestamp(t) for t in data[0]]

        ax1.set_facecolor('#454545')
        ax1.tick_params(labelcolor='tab:orange')
        ax1.plot(x_time, data[1], label=self.columns[0])
        ax1.plot(x_time, data[2], label=self.columns[1])
        ax1.plot(x_time, data[3], '--', label=self.columns[2])
        ax1.plot(x_time, data[4], '--', label=self.columns[3])
        ax1.grid(True, color='#353535')
        ax1.legend(fancybox=True, framealpha=0.1, labelcolor='tab:orange')

        ax2.set_facecolor('#454545')
        ax2.tick_params(labelcolor='tab:orange')
        ax2.plot(x_time, data[5], '--', label=self.columns[4], linewidth=2)
        ax2.plot(x_time, data[6]+0.01, label=self.columns[5])
        ax2.plot(x_time, data[7]+0.02, label=self.columns[6])
        ax2.plot(x_time, data[8]+0.03, label=self.columns[7])
        ax2.set_ylim(-0.1,1.1)
        ax2.grid(True, color='#353535')
        ax2.legend(fancybox=True, framealpha=0.1, labelcolor='tab:orange')

        fig_url = '/static/images/plot.png'
        plt.savefig('flaskr'+fig_url)
        return fig_url



