from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class users_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.username = name

class lootTables_db(db.Model):
    tableid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer)
    shareable = db.Column(db.Boolean)

    def __init__(self, userid):
        self.userid = userid
        self.shareable = 1

class loot_db(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tableid = db.Column(db.Integer)
    character = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    itemid = db.Column(db.Integer)

    def __init__(self, tableid, character, date, itemid):
        self.tableid = tableid
        self.character = character
        self.date = date
        self.itemid = itemid
