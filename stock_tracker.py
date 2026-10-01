import yfinance as yf
import requests
import sys
import time as time_module
from datetime import datetime, time
from zoneinfo import ZoneInfo


# ============================================================
# FIX WINDOWS UTF-8 / EMOJI ERROR
# ============================================================

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# TELEGRAM SETTINGS
# ============================================================

BOT_TOKEN = "8752288484:AAEASSBGOBjxEbIGOOo1jRu7t9S88s4FVzs"
CHAT_ID = "7115320700"


# ============================================================
# TIMEZONE
# ============================================================

TIMEZONE = ZoneInfo("Asia/Kolkata")


# ============================================================
# YOUR STOCKS
# ============================================================

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


# ============================================================
# TELEGRAM FUNCTION
# ============================================================

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        if response.status_code == 200:

            print("✅ Telegram message sent successfully.")

        else:

            print("❌ Telegram error:")
            print(response.text)

    except Exception as e:

        print("❌ Could not send Telegram message:")
        print(e)


# ============================================================
# CHECK WHETHER NSE MARKET IS OPEN
# ============================================================

def is_market_open():

    now = datetime.now(TIMEZONE)

    # Monday = 0
    # Sunday = 6

    if now.weekday() >= 5:

        return False

    market_start = time(9, 15)
    market_end = time(15, 30)

    current_time = now.time()

    if market_start <= current_time <= market_end:

        return True

    return False


# ============================================================
# GET STOCK DATA
# ============================================================

def get_stock_data(stock):

    symbol = stock["symbol"]
    buy_price = stock["buy_price"]
    quantity = stock["quantity"]

    try:

        ticker = yf.Ticker(symbol)

        # Get today's 1-minute data
        data = ticker.history(
            period="1d",
            interval="1m"
        )

        if data.empty:

            raise Exception(
                f"No market data available for {symbol}"
            )

        # Current/latest price
        current_price = float(data["Close"].dropna().iloc[-1])

        # Day high
        day_high = float(data["High"].max())

        # Day low
        day_low = float(data["Low"].min())

        # Previous closing price
        daily_data = ticker.history(
            period="5d",
            interval="1d"
        )

        previous_close = None

        if len(daily_data) >= 2:

            previous_close = float(
                daily_data["Close"].iloc[-2]
            )

        # Profit / Loss per unit
        profit_loss_per_unit = current_price - buy_price

        # Total Profit / Loss
        total_profit_loss = (
            profit_loss_per_unit * quantity
        )

        # Total investment
        total_investment = buy_price * quantity

        # Current value
        current_value = current_price * quantity

        return {

            "current_price": current_price,
            "buy_price": buy_price,
            "quantity": quantity,
            "day_high": day_high,
            "day_low": day_low,
            "previous_close": previous_close,
            "profit_loss_per_unit": profit_loss_per_unit,
            "total_profit_loss": total_profit_loss,
            "total_investment": total_investment,
            "current_value": current_value

        }

    except Exception as e:

        print(f"❌ Error getting {symbol}:")
        print(e)

        return None


# ============================================================
# CREATE PORTFOLIO MESSAGE
# ============================================================

def create_message(all_data):

    now = datetime.now(TIMEZONE)

    message = ""

    message += "📊 MY STOCK PORTFOLIO\n"
    message += "==============================\n\n"

    message += (
        "🕒 "
        + now.strftime("%d-%m-%Y %I:%M:%S %p")
        + "\n\n"
    )

    total_investment = 0
    total_current_value = 0
    total_profit_loss = 0

    for name, data in all_data.items():

        if data is None:

            message += f"❌ {name}\n"
            message += "Unable to get stock data.\n\n"

            continue

        current_price = data["current_price"]
        buy_price = data["buy_price"]
        quantity = data["quantity"]
        day_high = data["day_high"]
        day_low = data["day_low"]
        previous_close = data["previous_close"]
        profit_loss_per_unit = data["profit_loss_per_unit"]
        total_profit_loss_stock = data["total_profit_loss"]
        total_investment_stock = data["total_investment"]
        current_value_stock = data["current_value"]

        message += f"📌 {name}\n"
        message += "------------------------------\n"

        message += (
            f"Current Price: ₹{current_price:.2f}\n"
        )

        message += (
            f"Buy Price/Unit: ₹{buy_price:.3f}\n"
        )

        message += (
            f"Quantity: {quantity}\n"
        )

        message += (
            f"P/L per Unit: ₹{profit_loss_per_unit:.2f}\n"
        )

        message += (
            f"Total P/L: ₹{total_profit_loss_stock:.2f}\n"
        )

        message += (
            f"Day High: ₹{day_high:.2f}\n"
        )

        message += (
            f"Day Low: ₹{day_low:.2f}\n"
        )

        if previous_close is not None:

            message += (
                f"Previous Close: "
                f"₹{previous_close:.2f}\n"
            )

        message += (
            f"Investment: ₹{total_investment_stock:.2f}\n"
        )

        message += (
            f"Current Value: ₹{current_value_stock:.2f}\n"
        )

        message += "\n"

        total_investment += total_investment_stock
        total_current_value += current_value_stock
        total_profit_loss += total_profit_loss_stock

    # Portfolio totals

    message += "==============================\n"
    message += "💰 PORTFOLIO TOTAL\n"
    message += "==============================\n"

    message += (
        f"Total Investment: "
        f"₹{total_investment:.2f}\n"
    )

    message += (
        f"Current Value: "
        f"₹{total_current_value:.2f}\n"
    )

    message += (
        f"Total P/L: "
        f"₹{total_profit_loss:.2f}\n"
    )

    return message


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("MY STOCK PORTFOLIO TRACKER")
    print("=" * 60)

    print("Tracker started.")
    print("It will check your stocks every 5 minutes.")
    print("Press Ctrl+C to stop the program.")
    print("=" * 60)

    # --------------------------------------------------------
    # STARTUP TEST MESSAGE
    # --------------------------------------------------------

    startup_message = (
        "✅ Stock Portfolio Tracker started successfully!\n\n"
        "📅 Python program is running in the background.\n"
        "💻 Task Scheduler successfully started the tracker."
    )

    send_telegram_message(startup_message)

    # --------------------------------------------------------
    # CONTINUOUS LOOP
    # --------------------------------------------------------

    while True:

        try:

            now = datetime.now(TIMEZONE)

            print("\n")
            print("=" * 60)

            print(
                "Current time:",
                now.strftime("%d-%m-%Y %I:%M:%S %p")
            )

            print("=" * 60)

            # ------------------------------------------------
            # MARKET OPEN
            # ------------------------------------------------

            if is_market_open():

                print("🟢 Market is OPEN.")

                all_data = {}

                for name, stock in STOCKS.items():

                    print(
                        f"Getting data for {name}..."
                    )

                    all_data[name] = get_stock_data(
                        stock
                    )

                message = create_message(all_data)

                print("\nMessage:")
                print("-" * 60)

                print(message)

                print("-" * 60)

                send_telegram_message(message)

            # ------------------------------------------------
            # MARKET CLOSED
            # ------------------------------------------------

            else:

                print("⏸ Market is closed.")
                print(
                    "Waiting for the next check..."
                )

            # ------------------------------------------------
            # WAIT 5 MINUTES
            # ------------------------------------------------

            print("\n⏳ Next check in 5 minutes...")

            time_module.sleep(300)

        # ----------------------------------------------------
        # STOP WITH CTRL+C
        # ----------------------------------------------------

        except KeyboardInterrupt:

            print("\n")
            print("🛑 Stock tracker stopped.")

            break

        # ----------------------------------------------------
        # HANDLE OTHER ERRORS
        # ----------------------------------------------------

        except Exception as e:

            print("\n❌ Unexpected error:")
            print(e)

            print(
                "Retrying in 5 minutes..."
            )

            time_module.sleep(300)


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()