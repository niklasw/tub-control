import sys
from pathlib import Path
from flaskr import db

class logger:

    def __init__(self, log):
        self.logfile = Path(log)

