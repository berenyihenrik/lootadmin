from flask import Flask, session, redirect, request, render_template, make_response, url_for
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from flask_session import Session
from io import StringIO
import requests
import os

# own libraries
from read import *
from database import *

# Configuration
CLIENT_ID = "841369937188487199"
CLIENT_SECRET = "FfN8yhGDUcg9ZwmqgIYzMTTeVRBByt9A"

# Flask app setup
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Specifies the token cache should be stored in server-side session
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # a warning told me to do this
db = SQLAlchemy(app)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# OAuth 2 client setup
client = WebApplicationClient(CLIENT_ID)

users = [] # temporary userID storage

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri='http://localhost:5000/login/callback'
,
        auto_refresh_kwargs={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
        auto_refresh_url='https://discord.com/api/oauth2/token'
)


@app.route("/login") # login page; uses Discord OAuth2
def login():
    authorization_endpoint = 'https://discord.com/api/oauth2/authorize?client_id=841369937188487199&redirect_uri=https%3A%2F%2F0.0.0.0%3A5000%2Flogin%2Fcallback&response_type=code&scope=identify'

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback"
    )
    return redirect(request_uri)


@app.route("/login/callback") # login callback; handles token response
def callback():
    # Get authorization code
    code = request.args.get("code")

    # Prepare and send a request to get tokens! Yay tokens!
    API_ENDPOINT = 'https://discord.com/api/v8'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.base_url
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_response = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)

    # Parse the tokens!
    discord = make_session(token=token_response.json())
    user = discord.get(API_ENDPOINT + '/users/@me').json()

    resp = make_response(redirect(url_for("home")))
    resp.set_cookie('id', user['id'])
    users.append(user['id'])

    found_user = users_db.query.filter_by(id=request.cookies['id']).first()
    if found_user:
        print("user was already in the database")
    else:
        usr = users_db(user['id'], user['username'])
        db.session.add(usr)
        db.session.commit()
        print("added user to database")

    return resp


@app.route("/logout") # logout page; removes id from session cookie
def logout():
    if checkLogin(request, users):
        users.remove(request.cookies['id'])
        resp = make_response(redirect(url_for("home")))
        resp.set_cookie('id', '', expires=0)
    return resp


@app.route("/")
def home():
    if checkLogin(request, users):
        return redirect(url_for("tables"))
    else:
        return redirect("/login")

@app.route("/tables", methods=['GET', 'POST'])
def tables():
    if checkLogin(request, users):
        if request.method == 'POST':
            return redirect(url_for("input"))
        else:
            tables = []
            user = users_db.query.filter_by(id=request.cookies['id']).first()
            table = lootTables_db.query.filter_by(userid=user.id).all()
            for i in range(len(table)):
                tables.append(table[i].tableid)

            return render_template("tables.html", tables=tables)

    else:
        return redirect("/login")


@app.route("/input", methods=['GET', 'POST'])
def input():
    if checkLogin(request, users):
        if request.method == 'POST':
            session['csv'] = request.form.get('loot_csv')

            user = users_db.query.filter_by(id=request.cookies['id']).first()
            table = lootTables_db(user.id)
            db.session.add(table)
            db.session.commit()

            return redirect(url_for("loot"))

        return '<form method="POST"> <textarea class="textbox" type="textarea" name="loot_csv" placeholder="paste CSV here"> </textarea> <input class="button" type="submit" value="Submit"></form>'

    else:
        return redirect("/login")

@app.route("/loot/", methods=['GET', 'POST'])
def loot():
    if checkLogin(request, users):
        if request.method == 'POST':
            characters, dates = readDB(request.form.get('table'))
            print(characters)

        else:
            csv = session.get('csv', None)
            f = StringIO(csv)

            characters, dates = readrawcsv(f)

        return render_template('loot.html', characters=characters, len=len(characters), dates=dates, datelen=len(dates))

    else:
        return redirect("/login")

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', ssl_context="adhoc")


