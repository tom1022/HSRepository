import random, string, sys, threading
from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_session import Session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from .config import ConfigWatcher

app = Flask(__name__)

config_watcher = ConfigWatcher(app)
config_thread = threading.Thread(target=config_watcher.run)
config_thread.start()

Session(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db, render_as_batch=True)

from .models import tables

from dbapp.views.user import user_bp
app.register_blueprint(user_bp, url_prefix='/')

from dbapp.views.api import api
app.register_blueprint(api, url_prefix='/api')

from dbapp.views.auth import auth
app.register_blueprint(auth)

from dbapp.views.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from dbapp.views.logined import logined_bp
app.register_blueprint(logined_bp, url_prefix='/')

login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return tables.USERS.query.get(str(user_id))

@app.errorhandler(404)
def notfound(error):
    return render_template('errors/404.html'), 404

def generate_error_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

@app.errorhandler(500)
def internalError(error):
    error_id = generate_error_id()

    sys.stderr.write(f'Error ID: {error_id}\n')

    return render_template('errors/500.html', error_id=error_id), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.before_first_request
def init():
    try:
        tables.USERS.query.filter(tables.USERS.name=="admin").one_or_none()
    except Exception:
        db.create_all()
        admin_role = tables.ROLES(name='Admin')
        db.session.add(admin_role)
        db.session.commit()
        student_role = tables.ROLES(name='Student')
        db.session.add(student_role)
        db.session.commit()
        admin = tables.USERS(
            name='admin',
            display_name='Administrator',
            password=generate_password_hash('password')
        )
        admin.roles = [admin_role, student_role]
        db.session.add(admin)
        db.session.commit()

    return redirect(url_for('user_bp.index'))

from .tools import clean_html
from .tools import convertMarkdown

@app.context_processor
def global_variables():
    newslist = tables.NEWS.query.order_by(tables.NEWS.create_at.desc()).limit(5)
    title = config_watcher.get_config()['title']
    return {
        'newslist': newslist,
        'TITLE': title,
        'clean_html': clean_html,
        'convertMarkdown': convertMarkdown
    }