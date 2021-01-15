import sys

def Info(s, prompt='>>'):
    print('{} {}'.format(prompt, s))

def Debug(s):
    DEBUG = True if '-g' in sys.argv else False
    if DEBUG:
        Info(s, '>>>>\n')

def Error(s):
    Info(s,'Error:')


