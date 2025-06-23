from flask import Flask, render_template, request, redirect, session
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

# Setup logging
logging.basicConfig(filename='cookie_alert.log', level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        login_url = "https://api.bigdaddygame.cc/api/webapi/Login"
        payload = {
            "userName": username,
            "password": password
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': os.getenv('USER_AGENT')
        }

        res = requests.post(login_url, json=payload, headers=headers)
        if res.status_code == 200:
            token = res.json().get("data", {}).get("token")
            if token:
                session['access_token'] = token
                return redirect("/")
            else:
                return "Login failed: Token not found."
        else:
            return f"Login failed: {res.text}"

    return '''
        <form method="post">
            <label>Username: <input type="text" name="username"></label><br>
            <label>Password: <input type="password" name="password"></label><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/")
def home():
    token = session.get("access_token")
    if not token:
        return redirect("/login")

    headers = {
        'User-Agent': os.getenv('USER_AGENT'),
        'Authorization': f'Bearer {token}'
    }

    history_url = "https://www.bdggame3.com/api/WinGo/GetHistoryIssuePage?pageNo=1&pageSize=50"
    balance_url = "https://www.bdggame3.com/api/user/balance"

    try:
        # Fetch game history
        res = requests.get(history_url, headers=headers)

        # Check for expired token
        if res.status_code == 401:
            warning_message = "⚠️ Access token may have expired. Please log in again."
            logging.warning(warning_message)
            return redirect("/login")

        data = res.json()['data']['list']
        numbers = [int(item['number']) for item in data]
        big = [n for n in numbers if n >= 5]
        small = [n for n in numbers if n < 5]
        prediction = "Big" if len(big) > len(small) else "Small"

        # Fetch balance
        balance_res = requests.get(balance_url, headers=headers)
        balance = None
        if balance_res.status_code == 200:
            balance_data = balance_res.json()
            balance = balance_data.get("data", {}).get("balance")

        return render_template("index.html", results=numbers, prediction=prediction, balance=balance)

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
