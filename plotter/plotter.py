
import sqlite3
from relay.utils import *
from pathlib import Path
from datetime import datetime,timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

import numpy

def smooth(x,window_len=11, order=2):
    if len(x) < window_len:
        return x
    from scipy.signal import savgol_filter
    return savgol_filter(x, window_len, order)

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
        self.array_data = None

    def check_db_connection(self):
        if self.db:
            try:
                self.db.execute('PRAGMA user_version')
                return True
            except sqlite3.ProgrammingError as e:
                Debug('plotter.check_db_connection() returns False')
        return False

    def connect(self):
        if not self.check_db_connection():
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
        return self.db is not None

    def quit(self):
        if self.db:
            Info('Plotter disconnects from database')
            self.db.close()

    def set_time_range(self, dt, end_time=None):
        if end_time is None:
            end_time = datetime.now()
        self.start_time = (end_time - self.time_deltas[dt]).timestamp()
        self.end_time = end_time.timestamp()

    def get_data(self):
        if self.connect():
            list_fill = ', '.join(self.columns)
            sql = f'SELECT {list_fill} FROM "{self.table_name}" WHERE time >= {self.start_time} and time <= {self.end_time};'
            Debug(sql)
            Info(f'COLUMNS: {self.columns}')
            cursor = self.db.execute(sql)
            rows = cursor.fetchall()
            self.db.close()
            #max_points = 500
            #if len(rows) > 2*max_points:
            #    n_skip = int(len(rows)/max_points)
            #    rows = rows[0::n_skip]
            self.array_data = numpy.array(rows).transpose()
        else:
            self.array_data = numpy.array(len(self.columns)*[0])

    def ddt(self,column_name):
        data = self.array_data
        min_length = 25
        avg_length = 5

        if column_name in self.columns:
            index = self.columns.index(column_name)
            time = data[0]
            T = data[index]
            smoothT = smooth(T[-2*min_length:],11)
            time = time[-2*min_length:]
            ddt = 0
            if T.size >= min_length:
                dt = numpy.diff(time)
                dT = numpy.diff(smoothT)
                ddt = dT/dt
                ddt = numpy.average(ddt[-avg_length:])
            return ddt
        else:
            return 0


    def create_figure(self):
        fig, (ax1, ax2) = plt.subplots(nrows=2, \
                                       figsize=(12.96,8), \
                                       constrained_layout=True)
 
        fig.patch.set_alpha(0.0)
        ax1.patch.set_alpha(0.0)
        ax2.patch.set_alpha(0.0)
        try:
            data = self.array_data
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

            # ax1.set_facecolor('#454545')
            ax1.tick_params(labelcolor='tab:orange')
            ax1.plot(x_time, data[1], label=self.columns[1])
            ax1.plot(x_time, data[2], label=self.columns[2])
            ax1.plot(x_time, data[3], label=self.columns[3])
            ax1.plot(x_time, data[4], '--', label=self.columns[4])
            ax1.plot(x_time, data[5], '--', label=self.columns[5])
            ax1.grid(True, color='#353535')
            ax1.legend(fancybox=True, framealpha=0.1, labelcolor='tab:orange')

            #ax2.set_facecolor('#454545')
            ax2.tick_params(labelcolor='tab:orange')
            ax2.plot(x_time, data[6], '--', label=self.columns[6], linewidth=2)
            ax2.plot(x_time, data[7]+0.01, label=self.columns[7])
            ax2.plot(x_time, data[8]+0.02, label=self.columns[8])
            ax2.plot(x_time, data[9]+0.03, label=self.columns[9])
            ax2.set_ylim(-0.1,1.1)
            ax2.grid(True, color='#353535')
            ax2.legend(fancybox=True, framealpha=0.1, labelcolor='tab:orange')
        except:
            Warning('simple_plot failed')

        self.figure = fig

