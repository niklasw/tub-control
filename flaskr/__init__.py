from flask import Flask
from flask_htpasswd import HtPasswdAuth
from pathlib import Path

def create_app():
    app = Flask(__name__)
    
    app.config['FLASK_HTPASSWD_PATH'] = Path(Path.cwd(),'.htpasswd').as_posix()
    app.config['FLASK_SECRET'] = 'hey Hey Kids, secure me!'
    app.config['FLASK_AUTH_ALL']=True
    htpasswd = HtPasswdAuth(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

