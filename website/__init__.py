from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_toastr import Toastr
from flask_migrate import Migrate

basedir = os.getcwd()

# Initialize SQLAlchemy globally
db = SQLAlchemy()
migrate = Migrate()

# *Variables*
# ---- Database  ----
DB_FILE = os.getenv('DB_NAME', 'Database')  # DEV
url = 'sqlite:///' + os.path.join(basedir, str(DB_FILE) + '.sqlite3')
toastr = Toastr()

# *Create app definition*
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "adsbfioqwefhi1oi'23h21424@#F2#%ASRDaasd"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TOASTR_POSITION_CLASS'] = 'toast-bottom-right'
    app.config['SQLALCHEMY_DATABASE_URI'] = url
    toastr.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db) 

    from .blueprints.views import views

    try:
        create_databasemysql()
    except Exception as e_mysql:
        print("Erro ao conectar ao MySQL:", e_mysql)
        print(" ")

    app.register_blueprint(views)

    return app

# *Create Database*
def create_databasemysql():
    engine = create_engine(url)
    if not database_exists(engine.url):
        create_database(engine.url)
        with app.app_context():  # Create an application context
            db.create_all()
        print("*************Created Database!!*************")
    else:
        engine.connect()
        print("*************DB Connected!!*************")
