from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os

# Flask app setup
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Specifies the token cache should be stored in server-side session
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # a warning told me to do this
db = SQLAlchemy(app)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)