#!/usr/bin/env python3
"""
MT5 API Connector for FBS
Connects Python trading system to MT5 terminal
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import json

class MT5FBSConnector:
    def __init__(self):
        self.connected = False
        self.account_info = None
        
    def connect(self, login=None, password=None, server="FBS-Demo"):
        """Connect to MT5 terminal"""
        if not mt5.initialize():
            print("❌ MT5 initialization failed")
            return False
        
        if login and password:
            if not mt5.login(login, password=password, server=server):
                print(f"❌ Login failed: {mt5.last_error()}")
                return False
        
        self.connected = True
        self.account_info = mt5.account_info()
        print("✅ Connected to MT5")
        print(f"📊 Account: {self.account_info.login}")
        print(f"🏦 Server: {self.account_info.server}")
        print(f"💰 Balance: ${self.account_info.balance}")
        
        return True
    
    def get_account_info(self):
        """Get account information"""
        if not self.connected:
            return None
        
        info = mt5.account_info()
        return {
            "login": info.login,
            "server": info.server,
            "balance": info.balance,
            "equity": info.equity,
            "margin": info.margin,
            "free_margin": info.margin_free,
            "margin_level": info.margin_level,
            "currency": info.currency,
            "leverage": info.leverage,
            "profit": info.profit
        }
    
    def get_symbol_info(self, symbol):
        """Get symbol information"""
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
        
        return {
            "symbol": symbol,
            "bid": info.bid,
            "ask": info.ask,
            "spread": info.spread,
            "digits": info.digits,
            "point": info.point,
            "minimum_volume": info.volume_min,
            "maximum_volume": info.volume_max,
            "volume_step": info.volume_step
        }
    
    def get_rates(self, symbol, timeframe, count=100):
        """Get historical rates"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def place_order(self, symbol, order_type, volume, price=None, sl=None, tp=None, comment=""):
        """Place trading order"""
        if not self.connected:
            return None
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ Symbol {symbol} not found")
            return None
        
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                print(f"❌ Failed to select {symbol}")
                return None
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if price:
            request["price"] = price
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ Order failed: {result.retcode}")
            return None
        
        print(f"✅ Order placed: {result.order}")
        return result
    
    def get_positions(self):
        """Get open positions"""
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        return [{
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "BUY" if pos.type == 0 else "SELL",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "price_current": pos.price_current,
            "profit": pos.profit,
            "swap": pos.swap,
            "comment": pos.comment
        } for pos in positions]
    
    def close_position(self, ticket):
        """Close position by ticket"""
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        
        position = positions[0]
        
        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE
    
    def disconnect(self):
        """Disconnect from MT5"""
        mt5.shutdown()
        self.connected = False
        print("🔌 Disconnected from MT5")

# Example usage
def main():
    connector = MT5FBSConnector()
    
    print("🔌 MT5 FBS Connector Test")
    print("=" * 25)
    
    # Connect to MT5
    if not connector.connect():
        return
    
    # Get account info
    account = connector.get_account_info()
    print(f"\n📊 Account Info:")
    for key, value in account.items():
        print(f"  {key}: {value}")
    
    # Get EURUSD info
    symbol_info = connector.get_symbol_info("EURUSD")
    if symbol_info:
        print(f"\n💱 EURUSD Info:")
        for key, value in symbol_info.items():
            print(f"  {key}: {value}")
    
    # Get recent rates
    rates = connector.get_rates("EURUSD", mt5.TIMEFRAME_H1, 10)
    if rates is not None:
        print(f"\n📈 Recent EURUSD H1 Rates:")
        print(rates.tail())
    
    # Get positions
    positions = connector.get_positions()
    print(f"\n📋 Open Positions: {len(positions)}")
    
    connector.disconnect()

if __name__ == "__main__":
    main()