#!/usr/bin/env python3
"""
Capital.com API Integration
Full trading functionality for Capital.com CFD trading platform
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class CapitalComBroker:
    """Capital.com API client for trading operations"""
    
    def __init__(self):
        """Initialize Capital.com broker connection"""
        self.api_key = os.getenv('CAPITAL_COM_API_KEY', '')
        self.identifier = os.getenv('CAPITAL_COM_IDENTIFIER', '')
        self.password = os.getenv('CAPITAL_COM_PASSWORD', '')
        self.is_demo = os.getenv('CAPITAL_COM_DEMO', 'true').lower() == 'true'
        
        # Set API URL based on demo/live mode
        if self.is_demo:
            self.base_url = "https://demo-api-capital.backend-capital.com"
        else:
            self.base_url = "https://api-capital.backend-capital.com"
        
        self.session_token = None
        self.cst_token = None
        self.account_id = None
        
        logger.info(f"Initialized Capital.com broker ({'DEMO' if self.is_demo else 'LIVE'} mode)")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Capital.com API
        Returns: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/api/v1/session"
            
            payload = {
                "identifier": self.identifier,
                "password": self.password
            }
            
            headers = {
                "X-CAP-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                self.cst_token = response.headers.get('CST')
                self.session_token = response.headers.get('X-SECURITY-TOKEN')
                
                # Get account info
                data = response.json()
                self.account_id = data.get('accountId')
                
                logger.info(f"✅ Successfully authenticated with Capital.com (Account: {self.account_id})")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated request headers"""
        return {
            "X-SECURITY-TOKEN": self.session_token,
            "CST": self.cst_token,
            "Content-Type": "application/json"
        }
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information
        Returns: Account details dict or None
        """
        try:
            url = f"{self.base_url}/api/v1/accounts"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Account Balance: {data.get('balance', 'N/A')}")
                return data
            else:
                logger.error(f"Failed to get account info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def get_positions(self) -> Optional[List[Dict]]:
        """
        Get all open positions
        Returns: List of position dicts or None
        """
        try:
            url = f"{self.base_url}/api/v1/positions"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                positions = response.json().get('positions', [])
                logger.info(f"📈 Found {len(positions)} open position(s)")
                return positions
            else:
                logger.error(f"Failed to get positions: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return None
    
    def create_position(self, epic: str, direction: str, size: float, 
                       stop_loss: Optional[float] = None,
                       take_profit: Optional[float] = None) -> Optional[Dict]:
        """
        Create a new trading position
        
        Args:
            epic: Market identifier (e.g., 'EURUSD')
            direction: 'BUY' or 'SELL'
            size: Position size
            stop_loss: Stop loss level (optional)
            take_profit: Take profit level (optional)
            
        Returns: Position details dict or None
        """
        try:
            url = f"{self.base_url}/api/v1/positions"
            
            payload = {
                "epic": epic,
                "direction": direction.upper(),
                "size": size
            }
            
            if stop_loss:
                payload["stopLevel"] = stop_loss
            if take_profit:
                payload["profitLevel"] = take_profit
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                result = response.json()
                deal_ref = result.get('dealReference')
                logger.info(f"✅ Position created: {direction} {size} {epic} (Deal: {deal_ref})")
                return result
            else:
                logger.error(f"❌ Failed to create position: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating position: {str(e)}")
            return None
    
    def close_position(self, deal_id: str) -> bool:
        """
        Close an existing position
        
        Args:
            deal_id: Position deal ID
            
        Returns: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/api/v1/positions/{deal_id}"
            response = requests.delete(url, headers=self._get_headers())
            
            if response.status_code == 200:
                logger.info(f"✅ Position closed: {deal_id}")
                return True
            else:
                logger.error(f"❌ Failed to close position: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error closing position: {str(e)}")
            return False
    
    def update_position(self, deal_id: str, stop_loss: Optional[float] = None,
                       take_profit: Optional[float] = None) -> bool:
        """
        Update stop loss or take profit on existing position
        
        Args:
            deal_id: Position deal ID
            stop_loss: New stop loss level (optional)
            take_profit: New take profit level (optional)
            
        Returns: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/api/v1/positions/{deal_id}"
            
            payload = {}
            if stop_loss:
                payload["stopLevel"] = stop_loss
            if take_profit:
                payload["profitLevel"] = take_profit
            
            response = requests.put(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                logger.info(f"✅ Position updated: {deal_id}")
                return True
            else:
                logger.error(f"❌ Failed to update position: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating position: {str(e)}")
            return False
    
    def get_markets(self, search: str = "") -> Optional[List[Dict]]:
        """
        Search for available markets
        
        Args:
            search: Market search term (e.g., 'EUR', 'BTC')
            
        Returns: List of market dicts or None
        """
        try:
            url = f"{self.base_url}/api/v1/markets"
            params = {"searchTerm": search} if search else {}
            
            response = requests.get(url, params=params, headers=self._get_headers())
            
            if response.status_code == 200:
                markets = response.json().get('markets', [])
                logger.info(f"🔍 Found {len(markets)} market(s)")
                return markets
            else:
                logger.error(f"Failed to search markets: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching markets: {str(e)}")
            return None
    
    def get_market_details(self, epic: str) -> Optional[Dict]:
        """
        Get detailed market information
        
        Args:
            epic: Market identifier (e.g., 'EURUSD')
            
        Returns: Market details dict or None
        """
        try:
            url = f"{self.base_url}/api/v1/markets/{epic}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                market = response.json()
                logger.info(f"📊 Market: {epic} - Bid: {market.get('bid')} Ask: {market.get('ask')}")
                return market
            else:
                logger.error(f"Failed to get market details: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting market details: {str(e)}")
            return None
    
    def display_positions_summary(self):
        """Display formatted summary of all open positions"""
        positions = self.get_positions()
        
        if not positions:
            print("\n📊 No open positions")
            return
        
        print(f"\n{'='*80}")
        print(f"📈 OPEN POSITIONS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        for i, pos in enumerate(positions, 1):
            direction = pos.get('direction', 'N/A')
            epic = pos.get('market', {}).get('epic', 'N/A')
            size = pos.get('size', 0)
            open_level = pos.get('level', 0)
            current_level = pos.get('market', {}).get('bid' if direction == 'SELL' else 'ask', 0)
            pnl = pos.get('profit', 0)
            
            print(f"\n{i}. {epic}")
            print(f"   Direction: {direction} | Size: {size}")
            print(f"   Open: {open_level} | Current: {current_level}")
            print(f"   P&L: ${pnl:,.2f}")
            print(f"   Deal ID: {pos.get('dealId', 'N/A')}")
        
        print(f"\n{'='*80}\n")
