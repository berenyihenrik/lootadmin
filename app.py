from flask import Flask, g, session, redirect, request, render_template, make_response, url_for, send_from_directory
from oauthlib.oauth2 import WebApplicationClient
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session

import json
import re
import requests
import os

from csvMethods import *
from io import StringIO

# Configuration
CLIENT_ID = "841369937188487199"
CLIENT_SECRET = "FfN8yhGDUcg9ZwmqgIYzMTTeVRBByt9A"

# Flask app setup
app = Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# OAuth 2 client setup
client = WebApplicationClient(CLIENT_ID)

users = []

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


@app.route("/login")
def login():
    authorization_endpoint = 'https://discord.com/api/oauth2/authorize?client_id=841369937188487199&redirect_uri=https%3A%2F%2F0.0.0.0%3A5000%2Flogin%2Fcallback&response_type=code&scope=identify'

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback"
    )
    return redirect(request_uri)


@app.route("/login/callback")
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

    print(user)

    resp = make_response(redirect(url_for("home")))
    resp.set_cookie('id', user['id'])
    users.append(user['id'])

    return resp


@app.route("/logout")
def logout():
    if 'id' in request.cookies and request.cookies['id'] in users:
        users.remove(request.cookies['id'])
        resp = make_response(redirect(url_for("home")))
        resp.set_cookie('id', '', expires=0)
    return resp


@app.route("/")
def home():
    username = "world"
    if 'id' in request.cookies and request.cookies['id'] in users:
        return redirect(url_for("input"))
    else:
        return redirect("/login")


@app.route("/input", methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        session['csv'] = request.form.get('loot_csv')
        return redirect(url_for("loot"))
    
    return '<form method="POST"> <textarea class="textbox" type="textarea" name="loot_csv" placeholder="paste CSV here"> </textarea> <input class="button" type="submit" value="Submit"></form>'

@app.route("/loot/")
def loot():
    if 'id' not in request.cookies or request.cookies['id'] not in users:
        return 'no u'

    csv = session.get('csv', None)

    f = StringIO(csv)


    characters, dates = readrawcsv(f)


    return render_template('loot.html', characters=characters, len=len(characters), dates=dates, datelen=len(dates))


if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context="adhoc")
