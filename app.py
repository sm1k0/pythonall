from flask import Flask, render_template, request, redirect, url_for, flash, session
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=contract_address, abi=abi)

def is_strong_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*()-+=]', password):
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        public_key = request.form['public_key']
        password = request.form['password']
        try:
            w3.geth.personal.unlock_account(public_key, password)
            session['public_key'] = public_key
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Ошибка авторизации: {e}")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        if is_strong_password(password):
            try:
                account = w3.geth.personal.new_account(password)
                flash(f"Публичный ключ: {account}")
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"Ошибка регистрации: {e}")
        else:
            flash("Пароль слишком слабый.")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'public_key' not in session:
        return redirect(url_for('login'))
    account = session['public_key']
    balance = w3.eth.get_balance(account)
    contract_balance = contract.functions.getBalance().call({'from': account})
    return render_template('dashboard.html', account=account, balance=balance, contract_balance=contract_balance)

@app.route('/logout')
def logout():
    session.pop('public_key', None)
    return redirect(url_for('index'))

@app.route('/send_eth', methods=['POST'])
def send_eth():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    value = request.form['value']
    try:
        tx_hash = contract.functions.toPay(account).transact({
            "from": account,
            "value": int(value),
        })
        flash(f"Транзакция {tx_hash.hex()} отправлена")
    except Exception as e:
        flash(f"Ошибка отправки эфира: {e}")
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    amount = request.form['amount']
    try:
        tx_hash = contract.functions.withdraw(int(amount)).transact({'from': account})
        flash(f"Транзакция {tx_hash.hex()} отправлена")
    except Exception as e:
        flash(f"Ошибка снятия средств: {e}")
    return redirect(url_for('dashboard'))

@app.route('/create_estate', methods=['POST'])
def create_estate():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    size = request.form['size']
    estate_address = request.form['estate_address']
    es_type = request.form['es_type']
    try:
        tx_hash = contract.functions.createEstate(int(size), estate_address, int(es_type)).transact({'from': account})
        flash(f"Транзакция {tx_hash.hex()} отправлена для создания недвижимости")
    except Exception as e:
        flash(f"Ошибка создания недвижимости: {e}")
    return redirect(url_for('dashboard'))

@app.route('/create_ad', methods=['POST'])
def create_ad():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    id_estate = request.form['id_estate']
    price = request.form['price']
    try:
        tx_hash = contract.functions.createAd(int(id_estate), int(price)).transact({'from': account})
        flash(f"Транзакция {tx_hash.hex()} отправлена для создания объявления")
    except Exception as e:
        flash(f"Ошибка создания объявления: {e}")
    return redirect(url_for('dashboard'))

@app.route('/update_estate_status', methods=['POST'])
def update_estate_status():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    id_estate = request.form['id_estate']
    new_status = request.form['new_status']
    try:
        tx_hash = contract.functions.updateEstateStatus(int(id_estate), bool(int(new_status))).transact({'from': account})
        flash(f"Транзакция {tx_hash.hex()} отправлена для изменения статуса недвижимости")
    except Exception as e:
        flash(f"Ошибка изменения статуса недвижимости: {e}")
    return redirect(url_for('dashboard'))

@app.route('/update_ad_status', methods=['POST'])
def update_ad_status():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    id_ad = request.form['id_ad']
    new_status = request.form['new_status']
    try:
        tx_hash = contract.functions.updateAdStatus(int(id_ad), bool(int(new_status))).transact({'from': account})
        flash(f"Транзакция {tx_hash.hex()} отправлена для изменения статуса объявления")
    except Exception as e:
        flash(f"Ошибка изменения статуса объявления: {e}")
    return redirect(url_for('dashboard'))

@app.route('/get_estates_info')
def get_estates_info():
    try:
        estates = contract.functions.getEstates().call()
        estates_info = [{"ID": estate[5], "Размер": estate[0], "Адрес": estate[1], "Владелец": estate[2], "Тип": estate[3], "Статус": "Активен" if estate[4] else "Неактивен"} for estate in estates]
        return render_template('properties_info.html', estates=estates_info)
    except Exception as e:
        flash(f"Ошибка получения информации о недвижимости: {e}")
        return redirect(url_for('dashboard'))

@app.route('/get_ads_info')
def get_ads_info():
    try:
        ads = contract.functions.getAds().call()
        ads_info = [{"ID": ad[6], "Владелец": ad[0], "Цена": ad[2], "Недвижимость": ad[3], "Дата/время": ad[4], "Статус": "Открыто" if ad[5] else "Закрыто"} for ad in ads]
        return render_template('listings_info.html', ads=ads_info)
    except Exception as e:
        flash(f"Ошибка получения информации о текущих объявлениях: {e}")
        return redirect(url_for('dashboard'))

@app.route('/buy_estate', methods=['POST'])
def buy_estate():
    account = session.get('public_key')
    if not account:
        return redirect(url_for('login'))
    id_ad = request.form['id_ad']
    try:
        tx_hash = contract.functions.buyEstate(int(id_ad)).transact({'from': account, 'value': 0})
        flash(f"Транзакция {tx_hash.hex()} отправлена для покупки недвижимости")
    except Exception as e:
        flash(f"Ошибка покупки недвижимости: {e}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
