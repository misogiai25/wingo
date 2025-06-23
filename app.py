from flask import Flask, render_template
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

@app.route("/")
def home():
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    login_url = "https://api.bigdaddygame.cc/api/webapi/Login"
    payload = {
        "userName": username,
        "password": password
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': os.getenv('USER_AGENT')
    }

    login_res = requests.post(login_url, json=payload, headers=headers)
    if login_res.status_code != 200:
        return f"Login failed: {login_res.text}"

    response_data = login_res.json()
    token = response_data.get("data", {}).get("token") or response_data.get("data", {}).get("accessToken")
    if not token:
        return f"Login failed: Token not found. Full response: {response_data}"

    headers['Authorization'] = f'Bearer {token}'

    history_url = "https://www.bdggame3.com/api/WinGo/GetHistoryIssuePage?pageNo=1&pageSize=50"
    balance_url = "https://www.bdggame3.com/api/user/balance"

    try:
        # Fetch game history
        res = requests.get(history_url, headers=headers)
        if res.status_code == 401:
            warning_message = "⚠️ Access token may have expired."
            logging.warning(warning_message)
            return warning_message

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
