import yfinance as yf
import requests
import sys
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo
import os


# =========================================================
# TELEGRAM SETTINGS
# =========================================================

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


# =========================================================
# STOCK PORTFOLIO
# =========================================================

STOCKS = {
    "Urban Company": {
        "symbol": "URBANCO.NS",
        "buy_price": 168.85,
        "quantity": 1
    },

    "Tata Gold ETF": {
        "symbol": "TATAGOLD.NS",
        "buy_price": 7.425,
        "quantity": 2
    }
}


# =========================================================
# UTF-8 OUTPUT
# =========================================================

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# =========================================================
# MARKET STATUS
# =========================================================

def is_market_open():

    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    current_time = now.time()

    market_start = dt_time(9, 15)
    market_end = dt_time(15, 30)

    weekday = now.weekday()

    return (
        weekday < 5
        and market_start <= current_time <= market_end
    )


# =========================================================
# GET STOCK DATA
# =========================================================

def get_stock_data(symbol):

    ticker = yf.Ticker(symbol)

    intraday = ticker.history(
        period="1d",
        interval="1m"
    )

    daily = ticker.history(
        period="5d",
        interval="1d"
    )

    if intraday.empty:
        raise Exception(
            f"No intraday data available for {symbol}"
        )

    current_price = float(
        intraday["Close"].iloc[-1]
    )

    day_high = float(
        intraday["High"].max()
    )

    day_low = float(
        intraday["Low"].min()
    )

    if len(daily) >= 2:

        previous_close = float(
            daily["Close"].iloc[-2]
        )

    else:

        previous_close = current_price

    return {
        "current_price": current_price,
        "day_high": day_high,
        "day_low": day_low,
        "previous_close": previous_close
    }


# =========================================================
# CREATE PORTFOLIO MESSAGE
# =========================================================

def create_message():

    total_investment = 0
    total_current_value = 0

    message = (
        "📊 STOCK PORTFOLIO UPDATE\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for name, stock in STOCKS.items():

        data = get_stock_data(
            stock["symbol"]
        )

        current_price = data["current_price"]
        buy_price = stock["buy_price"]
        quantity = stock["quantity"]

        # Profit/Loss per unit
        profit_per_unit = (
            current_price - buy_price
        )

        # Total Profit/Loss
        total_profit = (
            profit_per_unit * quantity
        )

        # Investment amount
        investment = (
            buy_price * quantity
        )

        # Current value
        current_value = (
            current_price * quantity
        )

        # Day change
        day_change = (
            current_price
            - data["previous_close"]
        )

        if data["previous_close"] != 0:

            day_change_percent = (
                day_change
                / data["previous_close"]
                * 100
            )

        else:

            day_change_percent = 0

        total_investment += investment
        total_current_value += current_value

        message += (
            f"🔹 {name}\n\n"

            f"💰 Current Price: "
            f"₹{current_price:.2f}\n"

            f"🛒 Buy Price: "
            f"₹{buy_price:.3f}\n"

            f"📦 Quantity: "
            f"{quantity}\n\n"

            f"📈 P/L per Unit: "
            f"₹{profit_per_unit:.2f}\n"

            f"💵 Total P/L: "
            f"₹{total_profit:.2f}\n"

            f"📊 Day Change: "
            f"₹{day_change:.2f} "
            f"({day_change_percent:.2f}%)\n\n"

            f"🔺 Day High: "
            f"₹{data['day_high']:.2f}\n"

            f"🔻 Day Low: "
            f"₹{data['day_low']:.2f}\n"

            f"💼 Investment: "
            f"₹{investment:.2f}\n"

            f"💼 Current Value: "
            f"₹{current_value:.2f}\n\n"
        )

    # Portfolio total P/L
    total_profit = (
        total_current_value
        - total_investment
    )

    if total_investment != 0:

        total_profit_percent = (
            total_profit
            / total_investment
            * 100
        )

    else:

        total_profit_percent = 0

    message += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 PORTFOLIO TOTAL\n\n"

        f"💰 Total Investment: "
        f"₹{total_investment:.2f}\n"

        f"💼 Current Value: "
        f"₹{total_current_value:.2f}\n"

        f"📈 Total P/L: "
        f"₹{total_profit:.2f}\n"

        f"📊 Return: "
        f"{total_profit_percent:.2f}%\n"
    )

    return message


# =========================================================
# SEND TELEGRAM MESSAGE
# =========================================================

def send_telegram_message(message):

    telegram_url = (
        "https://api.telegram.org/bot"
        + BOT_TOKEN
        + "/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(
        telegram_url,
        data=data,
        timeout=20
    )

    if response.status_code == 200:

        print(
            "Telegram message sent successfully."
        )

    else:

        print(
            "Telegram error:"
        )

        print(
            response.text
        )


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    print("=" * 50)
    print("Stock Portfolio Tracker")
    print("=" * 50)

    try:

        current_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        print(
            "Current time:",
            current_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
        )

        # Check market status

        if is_market_open():

            print(
                "Market is OPEN."
            )

            # Create portfolio message
            message = create_message()

            # Send Telegram message
            send_telegram_message(
                message
            )

        else:

            print(
                "Market is CLOSED."
            )

            # Optional closed-market message
            message = (
                "⏸ Stock Portfolio Tracker\n\n"
                "🔴 Market is currently CLOSED.\n"
                "🇮🇳 NSE market hours: "
                "9:15 AM - 3:30 PM IST"
            )

            send_telegram_message(
                message
            )

    except Exception as error:

        print(
            "Error:"
        )

        print(
            error
        )


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    main()
