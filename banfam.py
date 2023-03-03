import os, requests, time
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, render_template, jsonify
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from models import db, login, UserModel

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'put_a_strong_key_here'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
@app.before_first_request
def create_table():
    db.create_all()
login.init_app(app)
login.login_view = 'login'

contestants = {'User1': 'put_user1_ban_address_here', 'User2': 'put_user2_ban_address_here', 'User3': 'put_user3_ban_address_here'}

def get_balances():
    balances = {k: '%.02f' % v for k, v in (sorted(({k:(float((requests.get('https://ban-api_domain_goes_here/?action=account_info&account=' + contestants[k]).json())['balance'])/100000000000000000000000000000) for (k,v) in contestants.items()}).items(), key=lambda item: item[1], reverse=True))}
    return balances

def get_prices():
    ban_cad = '%.08f' % (float(requests.get('https://api.coingecko.com/api/v3/simple/price?ids=banano&vs_currencies=cad').json()['banano']['cad']))
    ban_btc = '%.08f' % (float(requests.get('https://api.coingecko.com/api/v3/simple/price?ids=banano&vs_currencies=btc').json()['banano']['btc']))
    ban_doge = '%.08f' % (float(ban_cad)/requests.get('https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=cad').json()['dogecoin']['cad'])
    return {'ban_cad': ban_cad, 'ban_btc': ban_btc, 'ban_doge': ban_doge}

@app.route('/')
def home():
    balances = get_balances()
    prices = get_prices()
    monke = contestants[list(balances.keys())[0]]
    return render_template('home.html', title='name', balances=balances, prices=prices, monke=monke)

@app.route('/update_balances', methods=['GET'])
def update_balances():
    balances = get_balances()
    prices = get_prices()
    monke = "<img src='https://monkey.banano.cc/api/v1/monkey/" + contestants[list(balances.keys())[0]] + "?format=png&size=256&background=false' class='img-fluid'>"
    return jsonify(balances, prices, monke)

@app.route('/monkelogin', methods=['GET', 'POST'])
def monkelogin():
    if current_user.is_authenticated:
        return redirect('/apestats')

    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/apestats')

    return render_template('monkelogin.html')

@app.route('/aperegister', methods=['GET', 'POST'])
def aperegister():
    if current_user.is_authenticated:
        return redirect('/apestats')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return ('Ape already email')

        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/monkelogin')
    return render_template('aperegister.html')

@app.route('/logmonkeout')
def logmonkeout():
    logout_user()
    return redirect('/monkelogin')

@app.route('/apestats')
@login_required
def apestats():
    return render_template('apestats.html')

if __name__ == "__main__":
    app.run()
