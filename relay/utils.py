import sys
from pathlib import Path

def Info(s, prompt='>>'):
    print('{} {}'.format(prompt, s))

def Debug(s):
    DEBUG = True if '-g' in sys.argv else False
    if DEBUG:
        Info(s, '>>>>\n')

def Error(s):
    Info(s,'Error:')

class Configured:

    rid_pump = 0
    rid_heat = 1
    rid_aux = 2
    cwd = Path.cwd()
    database = cwd/'log'/'db.sql'
    db_table_name = 'history'
    err_temp = -100

    def log_row(self):
        print('ERROR: log_row() must be implemented in a Loggable class.')
        return []

    def log_data(self):
        print('ERROR: log_data() must be implemented in a Loggable class.')
        return OrderedDict()
