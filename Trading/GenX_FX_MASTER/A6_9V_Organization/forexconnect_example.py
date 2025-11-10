#!/usr/bin/env python3
"""
ForexConnect API Example
This example demonstrates basic ForexConnect API usage including:
- Session management
- Market data retrieval
- Account information
- Basic trading operations

Note: You need valid FXCM credentials to run this example.
"""

import forexconnect as fx
import time
import sys

class ForexConnectExample:
    def __init__(self):
        self.session = None
        self.login_descriptor = None
        
    def create_session(self):
        """Create and configure a ForexConnect session."""
        try:
            # Create session
            self.session = fx.O2GSession()
            
            # Create session descriptor
            self.login_descriptor = fx.O2GSessionDescriptor()
            
            print("✓ Session created successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error creating session: {e}")
            return False
    
    def configure_connection(self, url, username, password, connection_type="Demo"):
        """Configure connection parameters."""
        try:
            self.login_descriptor.setUrl(url)
            self.login_descriptor.setUser(username)
            self.login_descriptor.setPassword(password)
            self.login_descriptor.setConnection(connection_type)
            
            print(f"✓ Connection configured for {connection_type} environment")
            return True
            
        except Exception as e:
            print(f"✗ Error configuring connection: {e}")
            return False
    
    def connect(self):
        """Connect to FXCM servers."""
        try:
            # Note: This is just the connection setup
            # Actual login would require valid credentials
            print("✓ Connection parameters set up")
            print("  To actually connect, you would call:")
            print("  self.session.login(self.login_descriptor)")
            print("  (This requires valid FXCM credentials)")
            
            return True
            
        except Exception as e:
            print(f"✗ Error connecting: {e}")
            return False
    
    def get_market_data_info(self):
        """Show information about market data access."""
        print("\n=== Market Data Access ===")
        print("With a connected session, you can:")
        print("- Get real-time prices")
        print("- Access historical data")
        print("- Subscribe to price updates")
        
        example_code = '''
# Example market data operations (requires active session):

# Get offers table for currency pairs
offers_table = session.getTableManager().getTable(fx.O2GTableType.Offers)

# Get current bid/ask prices
for i in range(offers_table.size()):
    offer_row = offers_table.getRow(i)
    symbol = offer_row.getInstrument()
    bid = offer_row.getBid()
    ask = offer_row.getAsk()
    print(f"{symbol}: Bid={bid}, Ask={ask}")
'''
        print(example_code)
    
    def get_account_info(self):
        """Show information about account access."""
        print("\n=== Account Information Access ===")
        print("With a connected session, you can:")
        print("- Get account balance")
        print("- Check equity and margin")
        print("- View open positions")
        
        example_code = '''
# Example account operations (requires active session):

# Get accounts table
accounts_table = session.getTableManager().getTable(fx.O2GTableType.Accounts)

# Get account information
for i in range(accounts_table.size()):
    account_row = accounts_table.getRow(i)
    account_id = account_row.getAccountID()
    balance = account_row.getBalance()
    equity = account_row.getEquity()
    used_margin = account_row.getUsedMargin()
    
    print(f"Account: {account_id}")
    print(f"Balance: {balance}")
    print(f"Equity: {equity}")
    print(f"Used Margin: {used_margin}")
'''
        print(example_code)
    
    def show_trading_example(self):
        """Show trading operation examples."""
        print("\n=== Trading Operations ===")
        print("With a connected session, you can:")
        print("- Place market orders")
        print("- Set stop loss and take profit")
        print("- Manage positions")
        
        example_code = '''
# Example trading operations (requires active session):

# Create a market order
request_factory = session.getRequestFactory()

# Create buy order for EUR/USD
order_request = request_factory.createOrderRequest()
order_request.setInstrument("EUR/USD")
order_request.setCommand(fx.Constants.BUY)
order_request.setAmount(10000)  # 10K units
order_request.setOrderType(fx.Constants.MARKET_ORDER)
order_request.setAccountID("your_account_id")

# Send the order (this would actually place the trade)
# session.sendRequest(order_request)
'''
        print(example_code)
    
    def cleanup(self):
        """Clean up session resources."""
        try:
            if self.session:
                # In a real implementation, you would logout here
                # self.session.logout()
                print("✓ Session cleanup completed")
                
        except Exception as e:
            print(f"✗ Error during cleanup: {e}")

def main():
    """Main example function."""
    print("=== ForexConnect API Example ===\n")
    
    # Create example instance
    fx_example = ForexConnectExample()
    
    # Demonstrate session creation
    if not fx_example.create_session():
        print("Failed to create session")
        return
    
    # Demo connection configuration
    demo_url = "http://www.fxcorporate.com/Hosts.jsp"
    demo_username = "your_demo_username"  # Replace with your credentials
    demo_password = "your_demo_password"  # Replace with your credentials
    
    if not fx_example.configure_connection(demo_url, demo_username, demo_password):
        print("Failed to configure connection")
        return
    
    # Show connection (without actually connecting)
    if not fx_example.connect():
        print("Connection setup failed")
        return
    
    # Show various API capabilities
    fx_example.get_market_data_info()
    fx_example.get_account_info()
    fx_example.show_trading_example()
    
    # Cleanup
    fx_example.cleanup()
    
    print("\n=== Getting Started ===")
    print("1. Sign up for FXCM demo account: https://www.fxcm.com/")
    print("2. Replace the demo_username and demo_password with your credentials")
    print("3. Uncomment the actual connection and trading calls")
    print("4. Run this script to start trading!")
    
    print("\n=== Important Notes ===")
    print("- Always test with demo account first")
    print("- Implement proper error handling")
    print("- Use risk management in your trading strategies")
    print("- Check FXCM API documentation for complete reference")

if __name__ == "__main__":
    main()