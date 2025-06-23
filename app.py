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

@app.route("/")
def home():
    headers = {
        'User-Agent': os.getenv('USER_AGENT'),
        'Cookie': os.getenv('COOKIE')
    }

    api_url = "https://www.bdggame3.com/api/WinGo/GetHistoryIssuePage?pageNo=1&pageSize=50"

    try:
        res = requests.get(api_url, headers=headers)

        # Check for expired session (unauthorized or redirect to login)
        if res.status_code != 200 or 'login' in res.text.lower():
            warning_message = "⚠️ Cookie may have expired. Please update your COOKIE value in the .env file or environment settings."
            logging.warning(warning_message)
            return warning_message

        data = res.json()['data']['list']
        numbers = [int(item['number']) for item in data]

        big = [n for n in numbers if n >= 5]
        small = [n for n in numbers if n < 5]
        prediction = "Big" if len(big) > len(small) else "Small"

        return render_template("index.html", results=numbers, prediction=prediction)
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return f"Error fetching data: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
