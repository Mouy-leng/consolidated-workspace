"""
Order Execution and Management System
Handles order placement, tracking, and lifecycle management
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderManager:
    """Manages order execution and lifecycle"""
    
    def __init__(self, exchange_connector):
        self.exchange = exchange_connector
        self.active_orders = {}
        self.order_history = []
        self.is_monitoring = False
        
    async def place_market_order(self, symbol: str, side: str, amount: float, 
                                 metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Place a market order with tracking"""
        try:
            logger.info(f"Placing MARKET {side} order: {amount} {symbol}")
            
            # Create order
            order_result = await self.exchange.create_market_order(symbol, side, amount)
            
            if 'error' in order_result:
                logger.error(f"Order failed: {order_result['error']}")
                return {
                    'success': False,
                    'error': order_result['error']
                }
            
            # Track order
            order_id = order_result['id']
            self.active_orders[order_id] = {
                'order': order_result,
                'metadata': metadata or {},
                'created_at': datetime.now(),
                'last_update': datetime.now()
            }
            
            logger.info(f"Order placed successfully: {order_id}")
            
            # Monitor order execution
            await self.monitor_order(order_id, symbol)
            
            return {
                'success': True,
                'order_id': order_id,
                'order': order_result
            }
            
        except Exception as e:
            logger.error(f"Error placing market order: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
            
    async def place_limit_order(self, symbol: str, side: str, amount: float, price: float,
                               metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Place a limit order with tracking"""
        try:
            logger.info(f"Placing LIMIT {side} order: {amount} {symbol} @ {price}")
            
            # Create order
            order_result = await self.exchange.create_limit_order(symbol, side, amount, price)
            
            if 'error' in order_result:
                logger.error(f"Order failed: {order_result['error']}")
                return {
                    'success': False,
                    'error': order_result['error']
                }
            
            # Track order
            order_id = order_result['id']
            self.active_orders[order_id] = {
                'order': order_result,
                'metadata': metadata or {},
                'created_at': datetime.now(),
                'last_update': datetime.now()
            }
            
            logger.info(f"Order placed successfully: {order_id}")
            
            return {
                'success': True,
                'order_id': order_id,
                'order': order_result
            }
            
        except Exception as e:
            logger.error(f"Error placing limit order: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
            
    async def monitor_order(self, order_id: str, symbol: str, max_checks: int = 10):
        """Monitor order until filled or timeout"""
        try:
            for i in range(max_checks):
                await asyncio.sleep(2)  # Check every 2 seconds
                
                status = await self.exchange.get_order_status(order_id, symbol)
                
                if 'error' in status:
                    logger.error(f"Error checking order status: {status['error']}")
                    break
                
                logger.info(f"Order {order_id} status: {status['status']} - Filled: {status.get('filled', 0)}")
                
                # Update tracked order
                if order_id in self.active_orders:
                    self.active_orders[order_id]['order'].update(status)
                    self.active_orders[order_id]['last_update'] = datetime.now()
                
                # Check if order is complete
                if status['status'] in ['closed', 'filled']:
                    logger.info(f"Order {order_id} completed successfully")
                    await self.move_to_history(order_id)
                    break
                    
                if status['status'] in ['canceled', 'cancelled', 'expired']:
                    logger.warning(f"Order {order_id} was cancelled/expired")
                    await self.move_to_history(order_id)
                    break
                    
        except Exception as e:
            logger.error(f"Error monitoring order {order_id}: {e}", exc_info=True)
            
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an active order"""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            
            if 'error' not in result:
                logger.info(f"Order {order_id} cancelled successfully")
                await self.move_to_history(order_id)
                return True
            else:
                logger.error(f"Failed to cancel order: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}", exc_info=True)
            return False
            
    async def move_to_history(self, order_id: str):
        """Move order from active to history"""
        if order_id in self.active_orders:
            order_data = self.active_orders.pop(order_id)
            order_data['completed_at'] = datetime.now()
            self.order_history.append(order_data)
            logger.info(f"Order {order_id} moved to history")
            
    async def start_monitoring_loop(self):
        """Start continuous monitoring of all active orders"""
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                if self.active_orders:
                    logger.info(f"Monitoring {len(self.active_orders)} active orders")
                    
                    for order_id, order_data in list(self.active_orders.items()):
                        order = order_data['order']
                        symbol = order['symbol']
                        
                        # Check status
                        status = await self.exchange.get_order_status(order_id, symbol)
                        
                        if 'error' not in status:
                            order_data['order'].update(status)
                            order_data['last_update'] = datetime.now()
                            
                            # Handle completed orders
                            if status['status'] in ['closed', 'filled', 'canceled', 'cancelled']:
                                await self.move_to_history(order_id)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(5)
                
    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.is_monitoring = False
        logger.info("Order monitoring stopped")
        
    def get_active_orders(self) -> List[Dict]:
        """Get all active orders"""
        return list(self.active_orders.values())
        
    def get_order_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get order history"""
        if limit:
            return self.order_history[-limit:]
        return self.order_history
        
    def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics"""
        total_orders = len(self.order_history) + len(self.active_orders)
        filled_orders = len([o for o in self.order_history if o['order']['status'] in ['filled', 'closed']])
        
        return {
            'total_orders': total_orders,
            'active_orders': len(self.active_orders),
            'completed_orders': len(self.order_history),
            'filled_orders': filled_orders,
            'success_rate': filled_orders / total_orders if total_orders > 0 else 0
        }
