from flask import Flask, session, redirect, request, render_template, make_response, url_for
from io import StringIO
import requests

from app import app
from read import *
from auth import *

users = [] # temporary userID storage

@app.route("/login") # login page; uses Discord OAuth2
def login():
    authorization_endpoint = REDIRECT

    request_uri = client.prepare_request_uri(
        authorization_endpoint
    )
    return redirect(request_uri)


@app.route("/login/callback") # login callback; handles token response
def callback():
    # Get authorization code
    code = request.args.get("code")


    # Prepare and send a request to get tokens!
    API_ENDPOINT = 'https://discord.com/api/v8'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': CALLBACK
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

    found_user = users_db.query.filter_by(id=user['id']).first()
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

    return redirect("/login")

@app.route("/tables", methods=['GET', 'POST'])
def tables():
    if checkLogin(request, users):
        if request.method == 'POST':
            return redirect(url_for("input"))

        tables = []
        user = users_db.query.filter_by(id=request.cookies['id']).first()
        table = lootTables_db.query.filter_by(userid=user.id).all()
        for i in range(len(table)):
            tables.append(table[i].tableid)

        return render_template("tables.html", tables=tables)

    return redirect("/login")

@app.route("/input", methods=['GET', 'POST'])
def input():
    if checkLogin(request, users):
        if request.method == 'POST':
            session['csv'] = request.form.get('loot_csv')

            user = users_db.query.filter_by(id=request.cookies['id']).first()
            table = lootTables_db(user.id)
            session['table'] = table.tableid
            db.session.add(table)
            db.session.commit()

            tableid = table.tableid
            csv = request.form.get('loot_csv')
            f = StringIO(csv)
            readrawcsv(f, tableid)
            session['table'] = table.tableid

            return redirect(url_for("loot"))

        return render_template("input.html")

    return redirect("/login")

@app.route("/append", methods=['GET', 'POST'])
def append():
    if checkLogin(request, users):
        if request.method == 'POST':
            session['csv'] = request.form.get('loot_csv')

            table = lootTables_db.query.filter_by(tableid=session.get('table')).first()

            tableid = table.tableid
            csv = request.form.get('loot_csv')
            f = StringIO(csv)
            readrawcsv(f, tableid)
            session['table'] = table.tableid

            return redirect(url_for("loot"))

        print(session.get('table'))
        return render_template("append.html")

    return redirect("/login")

@app.route("/loot/", methods=['GET', 'POST'])
def loot():
    if checkLogin(request, users):
        if request.method == 'POST':
            session['table'] = request.form.get('table')

            return redirect(url_for("loot"))

        print("NONE", session.get('table'))
        characters, dates = readDB(session.get('table'))
        print(characters)
        return render_template('loot.html', characters=characters, len=len(characters), dates=dates, datelen=len(dates))

    else:
        return redirect("/login")


@app.route("/shared", methods=['GET'])
def shared():
    try:
        tableid = request.args.get('tableid')
        if lootTables_db.query.filter_by(tableid=tableid).first().shareable == 1:
            characters, dates = readDB(tableid)
            return render_template('sharedloot.html', characters=characters, len=len(characters), dates=dates, datelen=len(dates))

        return 'THIS TABLE IS ONLY AVAILABLE TO THE OWNER'

    except:
        return 'INVALID TABLE ID'