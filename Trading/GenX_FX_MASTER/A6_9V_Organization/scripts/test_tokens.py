import os
import requests
from dotenv import load_dotenv
import smtplib

load_dotenv()


def test_bybit():
    """Tests Bybit API connection."""
    print("Testing Bybit...")
    api_key = os.getenv("BYBIT_API_KEY")
    if not api_key:
        print("  ❌ BYBIT_API_KEY not found.")
        return

    # Use the v5 endpoint, as v2 is deprecated.
    url = "https://api.bybit.com/v5/market/time"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json().get("retCode") == 0:
            print("  ✅ Bybit connection successful.")
        else:
            status = response.status_code
            text = response.text[:150]
            print(
                f"  ❌ Bybit connection failed. Status: {status}, " f"Response: {text}"
            )
    except Exception as e:
        print(f"  ❌ Bybit connection error: {e}")


def test_telegram():
    """Tests Telegram Bot Token."""
    print("Testing Telegram...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("  ❌ TELEGRAM_BOT_TOKEN not found.")
        return

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            bot_name = data.get("result", {}).get("username")
            print(f"  ✅ Telegram connection successful for bot: @{bot_name}")
        else:
            status = response.status_code
            description = data.get("description", "No description provided.")
            print(
                f"  ❌ Telegram connection failed. Status: {status}, "
                f"Response: {description}"
            )
    except Exception as e:
        print(f"  ❌ Telegram connection error: {e}")


def test_gmail():
    """Tests Gmail App Password authentication."""
    print("Testing Gmail...")
    user = os.getenv("GMAIL_ADDRESS") or os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD") or os.getenv("GMAIL_APP_API_KEY")

    if not user or not password:
        print(
            "  ⚠️ GMAIL_ADDRESS/GMAIL_USER or GMAIL_APP_PASSWORD not found. " "Skipping."
        )
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            # The login test is the most reliable way to check credentials
            server.login(user, password)
            print(f"  ✅ Gmail authentication successful for {user}.")
    except smtplib.SMTPAuthenticationError:
        print(
            f"  ❌ Gmail authentication failed for {user}. " "Check GMAIL_APP_PASSWORD."
        )
    except smtplib.SMTPConnectError:
        print("  ❌ Could not connect to Gmail SMTP server. " "Check network/firewall.")
    except Exception as e:
        print(f"  ❌ Gmail connection error: {e}")


if __name__ == "__main__":
    print("--- Running Token Verification ---")
    if not os.path.exists(".env"):
        print(
            "⚠️ .env file not found. Make sure you copied .env.example "
            "to .env and filled it out."
        )
    else:
        test_bybit()
        test_telegram()
        test_gmail()
        # Add other token tests here (e.g., Alpha Vantage, FXCM, etc.)
    print("--- Verification Complete ---")
