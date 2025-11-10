import os
from pybit.unified_trading import HTTP

class BybitAPI:
    """
    A wrapper for the pybit library to interact with the Bybit V5 API.
    """
    def __init__(self):
        api_key = os.environ.get("BYBIT_API_KEY")
        api_secret = os.environ.get("BYBIT_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("BYBIT_API_KEY and BYBIT_API_SECRET environment variables must be set.")

        # For testnet, set testnet=True
        self.session = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )

    def get_market_data(self, symbol, interval, limit=200):
        """
        Fetches kline (market) data from Bybit V5 API.
        """
        try:
            response = self.session.get_kline(
                category="spot",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return response
        except Exception as e:
            print(f"Error fetching data from Bybit: {e}")
            return None

    def execute_order(self, symbol, side, order_type, qty):
        """
        Executes an order on Bybit V5 API.
        """
        try:
            response = self.session.place_order(
                category="spot",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=str(qty),
            )
            return response
        except Exception as e:
            print(f"Error executing order on Bybit: {e}")
            return None
