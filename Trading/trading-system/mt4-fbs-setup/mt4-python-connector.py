#!/usr/bin/env python3
"""
MT4 Python Connector for FBS
Uses DDE or file-based communication with MT4
"""

import os
import json
import time
import pandas as pd
from datetime import datetime
import subprocess

class MT4Connector:
    def __init__(self):
        self.login = "241926287"
        self.password = "f0v/9iIH"
        self.server = "FBS-Real-4"
        self.mt4_path = self.find_mt4_path()
        self.data_path = None
        
    def find_mt4_path(self):
        """Find MT4 installation path"""
        possible_paths = [
            "C:\\Program Files\\MetaTrader 4\\terminal.exe",
            "C:\\Program Files (x86)\\MetaTrader 4\\terminal.exe",
            os.path.expanduser("~\\AppData\\Local\\Programs\\MetaTrader 4\\terminal.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.data_path = os.path.dirname(path)
                return path
        
        return None
    
    def launch_mt4(self):
        """Launch MT4 with configuration"""
        if not self.mt4_path:
            print("MT4 not found")
            return False
        
        try:
            # Launch MT4
            subprocess.Popen([self.mt4_path])
            print("MT4 launched successfully")
            print(f"Login: {self.login}")
            print(f"Server: {self.server}")
            return True
        except Exception as e:
            print(f"Error launching MT4: {e}")
            return False
    
    def get_account_info(self):
        """Get account information (simulated)"""
        return {
            "login": self.login,
            "server": self.server,
            "company": "FBS Markets Inc.",
            "balance": 0.0,  # Will be updated from MT4
            "equity": 0.0,
            "margin": 0.0,
            "free_margin": 0.0,
            "connected": True
        }
    
    def get_symbol_info(self, symbol):
        """Get symbol information (simulated)"""
        # Common FBS symbols with approximate values
        symbols_data = {
            "EURUSD": {"bid": 1.0850, "ask": 1.0852, "digits": 5},
            "GBPUSD": {"bid": 1.2650, "ask": 1.2652, "digits": 5},
            "USDJPY": {"bid": 149.50, "ask": 149.52, "digits": 3},
            "XAUUSD": {"bid": 2025.50, "ask": 2026.50, "digits": 2},
            "XAGUSD": {"bid": 24.50, "ask": 24.52, "digits": 3}
        }
        
        return symbols_data.get(symbol, {"bid": 0, "ask": 0, "digits": 5})
    
    def create_ea_file(self):
        """Create Expert Advisor for Python communication"""
        ea_code = '''
//+------------------------------------------------------------------+
//| FBS Python Connector EA                                          |
//+------------------------------------------------------------------+
#property copyright "Trading System"
#property version   "1.00"

string dataFile = "mt4_data.csv";
string signalFile = "mt4_signals.csv";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("FBS Python Connector EA Started");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Export market data every 10 seconds
   static datetime lastUpdate = 0;
   if(TimeCurrent() - lastUpdate >= 10)
   {
      ExportMarketData();
      CheckSignals();
      lastUpdate = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Export market data to CSV                                        |
//+------------------------------------------------------------------+
void ExportMarketData()
{
   int handle = FileOpen(dataFile, FILE_WRITE|FILE_CSV);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, "Symbol,Bid,Ask,Time,Balance,Equity");
      
      string symbols[] = {"EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "XAGUSD"};
      
      for(int i = 0; i < ArraySize(symbols); i++)
      {
         double bid = MarketInfo(symbols[i], MODE_BID);
         double ask = MarketInfo(symbols[i], MODE_ASK);
         
         FileWrite(handle, symbols[i], bid, ask, TimeToStr(TimeCurrent()), 
                  AccountBalance(), AccountEquity());
      }
      
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Check for Python signals                                         |
//+------------------------------------------------------------------+
void CheckSignals()
{
   int handle = FileOpen(signalFile, FILE_READ|FILE_CSV);
   if(handle != INVALID_HANDLE)
   {
      while(!FileIsEnding(handle))
      {
         string symbol = FileReadString(handle);
         string action = FileReadString(handle);
         double lots = FileReadNumber(handle);
         
         if(symbol != "" && action != "")
         {
            ExecuteSignal(symbol, action, lots);
         }
      }
      FileClose(handle);
      
      // Clear signals file
      FileDelete(signalFile);
   }
}

//+------------------------------------------------------------------+
//| Execute trading signal                                           |
//+------------------------------------------------------------------+
void ExecuteSignal(string symbol, string action, double lots)
{
   int ticket = -1;
   double price = 0;
   
   if(action == "BUY")
   {
      price = MarketInfo(symbol, MODE_ASK);
      ticket = OrderSend(symbol, OP_BUY, lots, price, 3, 0, 0, "Python Signal", 0, 0, clrGreen);
   }
   else if(action == "SELL")
   {
      price = MarketInfo(symbol, MODE_BID);
      ticket = OrderSend(symbol, OP_SELL, lots, price, 3, 0, 0, "Python Signal", 0, 0, clrRed);
   }
   
   if(ticket > 0)
   {
      Print("Order executed: ", action, " ", symbol, " ", lots, " lots");
   }
   else
   {
      Print("Order failed: ", GetLastError());
   }
}
'''
        
        # Save EA file
        ea_path = os.path.join(self.data_path, "MQL4", "Experts", "FBS_Python_Connector.mq4")
        os.makedirs(os.path.dirname(ea_path), exist_ok=True)
        
        with open(ea_path, 'w') as f:
            f.write(ea_code)
        
        print(f"Expert Advisor created: {ea_path}")
        return ea_path
    
    def send_signal(self, symbol, action, lots=0.01):
        """Send trading signal to MT4"""
        if not self.data_path:
            return False
        
        signal_file = os.path.join(self.data_path, "Files", "mt4_signals.csv")
        os.makedirs(os.path.dirname(signal_file), exist_ok=True)
        
        try:
            with open(signal_file, 'w') as f:
                f.write(f"{symbol},{action},{lots}\n")
            
            print(f"Signal sent: {action} {symbol} {lots} lots")
            return True
        except Exception as e:
            print(f"Error sending signal: {e}")
            return False
    
    def read_market_data(self):
        """Read market data from MT4"""
        if not self.data_path:
            return None
        
        data_file = os.path.join(self.data_path, "Files", "mt4_data.csv")
        
        try:
            if os.path.exists(data_file):
                df = pd.read_csv(data_file)
                return df
        except Exception as e:
            print(f"Error reading market data: {e}")
        
        return None

def main():
    connector = MT4Connector()
    
    print("MT4 FBS Connector")
    print("=" * 20)
    
    # Launch MT4
    if connector.launch_mt4():
        print("MT4 launched successfully")
        
        # Create EA
        connector.create_ea_file()
        
        # Show account info
        account = connector.get_account_info()
        print(f"\nAccount Info:")
        for key, value in account.items():
            print(f"  {key}: {value}")
        
        # Test symbol info
        symbols = ["EURUSD", "XAUUSD", "GBPUSD"]
        print(f"\nSymbol Info:")
        for symbol in symbols:
            info = connector.get_symbol_info(symbol)
            print(f"  {symbol}: Bid={info['bid']}, Ask={info['ask']}")
        
        print(f"\nMT4 is ready for trading!")
        print(f"Use connector.send_signal('EURUSD', 'BUY', 0.01) to place orders")
    
    else:
        print("Failed to launch MT4")

if __name__ == "__main__":
    main()