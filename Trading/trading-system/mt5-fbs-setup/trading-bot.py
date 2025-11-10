#!/usr/bin/env python3
"""
FBS Trading Bot - Automated Trading System
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json

class FBSTradingBot:
    def __init__(self):
        self.login = 40933210
        self.password = "8IA.KFIB"
        self.server = "FBS-Real"
        self.connected = False
        self.risk_per_trade = 0.02  # 2% risk per trade
        
    def connect(self):
        """Connect to FBS MT5 account"""
        if not mt5.initialize():
            print("MT5 initialization failed")
            return False
        
        if not mt5.login(self.login, password=self.password, server=self.server):
            print(f"Login failed: {mt5.last_error()}")
            return False
        
        self.connected = True
        account_info = mt5.account_info()
        print(f"Connected to FBS Real Account")
        print(f"Balance: ${account_info.balance:.2f}")
        print(f"Equity: ${account_info.equity:.2f}")
        return True
    
    def get_account_info(self):
        """Get current account information"""
        if not self.connected:
            return None
        
        info = mt5.account_info()
        return {
            "balance": info.balance,
            "equity": info.equity,
            "margin": info.margin,
            "free_margin": info.margin_free,
            "profit": info.profit
        }
    
    def calculate_lot_size(self, symbol, stop_loss_pips):
        """Calculate lot size based on risk management"""
        account_info = mt5.account_info()
        balance = account_info.balance
        
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return 0.01
        
        risk_amount = balance * self.risk_per_trade
        pip_value = symbol_info.trade_tick_value
        
        if stop_loss_pips > 0:
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        else:
            lot_size = symbol_info.volume_min
        
        return round(lot_size, 2)
    
    def place_buy_order(self, symbol, lot_size, sl_pips=50, tp_pips=100):
        """Place buy order"""
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return None
        
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - (sl_pips * symbol_info.point)
        tp = price + (tp_pips * symbol_info.point)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "FBS Bot Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"BUY order placed: {symbol} {lot_size} lots at {price}")
            return result
        else:
            print(f"Order failed: {result.retcode}")
            return None
    
    def place_sell_order(self, symbol, lot_size, sl_pips=50, tp_pips=100):
        """Place sell order"""
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return None
        
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + (sl_pips * symbol_info.point)
        tp = price - (tp_pips * symbol_info.point)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "FBS Bot Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"SELL order placed: {symbol} {lot_size} lots at {price}")
            return result
        else:
            print(f"Order failed: {result.retcode}")
            return None
    
    def get_positions(self):
        """Get current open positions"""
        positions = mt5.positions_get()
        if not positions:
            return []
        
        return [{
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "BUY" if pos.type == 0 else "SELL",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "price_current": pos.price_current,
            "profit": pos.profit,
            "sl": pos.sl,
            "tp": pos.tp
        } for pos in positions]
    
    def simple_trading_strategy(self, symbol="EURUSD"):
        """Simple RSI-based trading strategy"""
        # Get recent price data
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
        if rates is None:
            return
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Check for existing positions
        positions = self.get_positions()
        has_position = any(pos['symbol'] == symbol for pos in positions)
        
        if not has_position:
            lot_size = self.calculate_lot_size(symbol, 50)
            
            # Buy signal: RSI oversold
            if current_rsi < 30:
                print(f"RSI Oversold ({current_rsi:.1f}) - Placing BUY order")
                self.place_buy_order(symbol, lot_size)
            
            # Sell signal: RSI overbought
            elif current_rsi > 70:
                print(f"RSI Overbought ({current_rsi:.1f}) - Placing SELL order")
                self.place_sell_order(symbol, lot_size)
        
        print(f"{symbol} RSI: {current_rsi:.1f}")
    
    def run_bot(self, symbols=["EURUSD", "GBPUSD", "XAUUSD"]):
        """Run the trading bot"""
        if not self.connect():
            return
        
        print("FBS Trading Bot Started")
        print("=" * 25)
        
        try:
            while True:
                print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Display account info
                account = self.get_account_info()
                print(f"Balance: ${account['balance']:.2f}, Equity: ${account['equity']:.2f}")
                
                # Run strategy for each symbol
                for symbol in symbols:
                    self.simple_trading_strategy(symbol)
                
                # Display positions
                positions = self.get_positions()
                print(f"Open positions: {len(positions)}")
                for pos in positions:
                    print(f"  {pos['symbol']} {pos['type']} {pos['volume']} lots, P&L: ${pos['profit']:.2f}")
                
                # Wait 5 minutes
                time.sleep(300)
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
        finally:
            mt5.shutdown()

def main():
    bot = FBSTradingBot()
    bot.run_bot()

if __name__ == "__main__":
    main()