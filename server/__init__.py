from flask import Flask
from server.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_admin import Admin
from .routes import main
from lyrica.routes import lyrica


app = Flask(__name__)
app.config.from_object(Config)
# jwt = JWTManager(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db, render_as_batch=True)

app.register_blueprint(lyrica)
app.register_blueprint(main)
