"""
TCP/IP Socket Communication Service for MT4/MT5 Expert Advisor Integration.
Provides real-time signal transmission and trade feedback between Python AI and MQL EAs.
"""

import asyncio
import json
import logging
import socket
import struct
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import threading
from queue import Queue, Empty
from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """Trading signal structure for EA communication"""
    signal_id: str
    instrument: str
    action: str  # "BUY", "SELL", "CLOSE", "CLOSE_ALL"
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    magic_number: int = 12345
    comment: str = "GenX AI Signal"
    timestamp: datetime = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingSignal':
        """Create signal from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class TradeResult:
    """Trade execution result from EA"""
    signal_id: str
    ticket: Optional[int]
    success: bool
    error_code: int = 0
    error_message: str = ""
    execution_price: Optional[float] = None
    execution_time: datetime = None
    slippage: float = 0.0
    
    def __post_init__(self):
        if self.execution_time is None:
            self.execution_time = datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeResult':
        """Create result from dictionary"""
        if 'execution_time' in data and isinstance(data['execution_time'], str):
            data['execution_time'] = datetime.fromisoformat(data['execution_time'])
        return cls(**data)


@dataclass
class AccountStatus:
    """Account status update from EA"""
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    open_positions: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountStatus':
        """Create status from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class MessageProtocol:
    """Message protocol for EA communication"""
    
    @staticmethod
    def encode_message(message_type: str, data: Dict[str, Any]) -> bytes:
        """
        Encode message for transmission to EA
        Format: [4-byte length][message_type][json_data]
        """
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        json_data = json.dumps(message).encode('utf-8')
        length = struct.pack('!I', len(json_data))
        
        return length + json_data
    
    @staticmethod
    def decode_message(data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode message from EA
        Returns None if message is incomplete or invalid
        """
        try:
            if len(data) < 4:
                return None
            
            # Extract length
            length = struct.unpack('!I', data[:4])[0]
            
            if len(data) < 4 + length:
                return None  # Incomplete message
            
            # Extract JSON data
            json_data = data[4:4+length].decode('utf-8')
            message = json.loads(json_data)
            
            return message
            
        except (struct.error, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error decoding message: {e}")
            return None


class EAConnection:
    """Individual EA connection handler"""
    
    def __init__(self, client_socket: socket.socket, address: tuple, server: 'EAServer'):
        self.socket = client_socket
        self.address = address
        self.server = server
        self.is_connected = True
        self.buffer = b''
        self.ea_info = {}
        
        # Start receiving messages
        self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self.receive_thread.start()
        
        logger.info(f"New EA connection from {address}")
    
    def _receive_messages(self):
        """Receive messages from EA in separate thread"""
        try:
            while self.is_connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break
                    
                    self.buffer += data
                    self._process_buffer()
                    
                except socket.timeout:
                    continue  # Continue receiving
                except Exception as e:
                    logger.error(f"Error receiving from EA {self.address}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error in receive thread for {self.address}: {e}")
        finally:
            self._disconnect()
    
    def _process_buffer(self):
        """Process received data buffer"""
        while len(self.buffer) >= 4:
            # Try to decode a complete message
            message = MessageProtocol.decode_message(self.buffer)
            
            if message is None:
                break  # Incomplete message, wait for more data
            
            # Calculate message length and remove from buffer
            length = struct.unpack('!I', self.buffer[:4])[0]
            self.buffer = self.buffer[4 + length:]
            
            # Process the message
            asyncio.run_coroutine_threadsafe(
                self.server._handle_message(message, self),
                self.server.loop
            )
    
    async def send_signal(self, signal: TradingSignal) -> bool:
        """Send trading signal to EA"""
        try:
            message_data = signal.to_dict()
            encoded_message = MessageProtocol.encode_message("SIGNAL", message_data)
            
            self.socket.send(encoded_message)
            logger.info(f"Signal sent to EA {self.address}: {signal.action} {signal.instrument}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending signal to EA {self.address}: {e}")
            return False
    
    async def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Send command to EA"""
        try:
            command_data = {
                "command": command,
                "parameters": params or {}
            }
            encoded_message = MessageProtocol.encode_message("COMMAND", command_data)
            
            self.socket.send(encoded_message)
            logger.info(f"Command sent to EA {self.address}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to EA {self.address}: {e}")
            return False
    
    def _disconnect(self):
        """Disconnect from EA"""
        if self.is_connected:
            self.is_connected = False
            try:
                self.socket.close()
            except:
                pass
            
            self.server._remove_connection(self)
            logger.info(f"EA disconnected: {self.address}")


class EAServer:
    """TCP server for EA connections"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9090):
        self.host = host
        self.port = port
        self.server_socket = None
        self.connections: List[EAConnection] = []
        self.is_running = False
        self.loop = None
        
        # Callbacks for different message types
        self.callbacks = {
            "TRADE_RESULT": [],
            "ACCOUNT_STATUS": [],
            "HEARTBEAT": [],
            "ERROR": []
        }
        
        # Signal queue for broadcasting
        self.signal_queue = Queue()
        
    async def start(self):
        """Start the EA server"""
        try:
            self.loop = asyncio.get_event_loop()
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.settimeout(1.0)  # Non-blocking accept
            
            self.is_running = True
            
            logger.info(f"EA Server started on {self.host}:{self.port}")
            
            # Start accepting connections
            await self._accept_connections()
            
        except Exception as e:
            logger.error(f"Error starting EA server: {e}")
            raise
    
    async def stop(self):
        """Stop the EA server"""
        self.is_running = False
        
        # Disconnect all EAs
        for connection in self.connections.copy():
            connection._disconnect()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("EA Server stopped")
    
    async def _accept_connections(self):
        """Accept incoming EA connections"""
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(30.0)  # 30 second timeout for EA operations
                
                # Create new connection
                connection = EAConnection(client_socket, address, self)
                self.connections.append(connection)
                
            except socket.timeout:
                # Check for pending signals to broadcast
                await self._process_signal_queue()
                continue
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting connection: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_signal_queue(self):
        """Process queued signals for broadcasting"""
        try:
            while not self.signal_queue.empty():
                signal = self.signal_queue.get_nowait()
                await self.broadcast_signal(signal)
        except Empty:
            pass
    
    def _remove_connection(self, connection: EAConnection):
        """Remove a disconnected connection"""
        if connection in self.connections:
            self.connections.remove(connection)
    
    async def _handle_message(self, message: Dict[str, Any], connection: EAConnection):
        """Handle incoming message from EA"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "TRADE_RESULT":
                trade_result = TradeResult.from_dict(data)
                await self._notify_callbacks("TRADE_RESULT", trade_result, connection)
                
            elif message_type == "ACCOUNT_STATUS":
                account_status = AccountStatus.from_dict(data)
                await self._notify_callbacks("ACCOUNT_STATUS", account_status, connection)
                
            elif message_type == "HEARTBEAT":
                # Update EA info
                connection.ea_info.update(data)
                await self._notify_callbacks("HEARTBEAT", data, connection)
                
            elif message_type == "ERROR":
                logger.error(f"EA Error from {connection.address}: {data}")
                await self._notify_callbacks("ERROR", data, connection)
                
            elif message_type == "EA_INFO":
                # Store EA information
                connection.ea_info = data
                logger.info(f"EA Info from {connection.address}: {data}")
                
            else:
                logger.warning(f"Unknown message type from EA {connection.address}: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message from EA {connection.address}: {e}")
    
    async def _notify_callbacks(self, message_type: str, data: Any, connection: EAConnection):
        """Notify registered callbacks"""
        for callback in self.callbacks.get(message_type, []):
            try:
                await callback(data, connection)
            except Exception as e:
                logger.error(f"Error in callback for {message_type}: {e}")
    
    def subscribe_to_trade_results(self, callback: Callable[[TradeResult, EAConnection], None]):
        """Subscribe to trade execution results"""
        self.callbacks["TRADE_RESULT"].append(callback)
    
    def subscribe_to_account_status(self, callback: Callable[[AccountStatus, EAConnection], None]):
        """Subscribe to account status updates"""
        self.callbacks["ACCOUNT_STATUS"].append(callback)
    
    def subscribe_to_heartbeat(self, callback: Callable[[Dict, EAConnection], None]):
        """Subscribe to EA heartbeat messages"""
        self.callbacks["HEARTBEAT"].append(callback)
    
    def subscribe_to_errors(self, callback: Callable[[Dict, EAConnection], None]):
        """Subscribe to EA error messages"""
        self.callbacks["ERROR"].append(callback)
    
    async def send_signal_to_ea(self, signal: TradingSignal, ea_address: tuple = None) -> bool:
        """Send signal to specific EA or all EAs"""
        if ea_address:
            # Send to specific EA
            for connection in self.connections:
                if connection.address == ea_address:
                    return await connection.send_signal(signal)
            return False
        else:
            # Broadcast to all EAs
            return await self.broadcast_signal(signal)
    
    async def broadcast_signal(self, signal: TradingSignal) -> bool:
        """Broadcast signal to all connected EAs"""
        if not self.connections:
            logger.warning("No EAs connected to receive signal")
            return False
        
        success_count = 0
        for connection in self.connections:
            if await connection.send_signal(signal):
                success_count += 1
        
        logger.info(f"Signal broadcasted to {success_count}/{len(self.connections)} EAs")
        return success_count > 0
    
    async def send_command_to_all(self, command: str, params: Dict[str, Any] = None) -> int:
        """Send command to all connected EAs"""
        success_count = 0
        for connection in self.connections:
            if await connection.send_command(command, params):
                success_count += 1
        
        return success_count
    
    def get_connected_eas(self) -> List[Dict[str, Any]]:
        """Get information about connected EAs"""
        ea_list = []
        for connection in self.connections:
            ea_info = {
                "address": connection.address,
                "connected": connection.is_connected,
                "info": connection.ea_info
            }
            ea_list.append(ea_info)
        
        return ea_list
    
    def queue_signal(self, signal: TradingSignal):
        """Queue signal for broadcasting (thread-safe)"""
        self.signal_queue.put(signal)


class EAClient:
    """Client for testing EA server connection"""
    
    def __init__(self, host: str = "localhost", port: int = 9090):
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to EA server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            
            # Send EA info
            ea_info = {
                "name": "Test EA",
                "version": "1.0",
                "account": "12345",
                "broker": "Test Broker"
            }
            
            await self.send_message("EA_INFO", ea_info)
            logger.info(f"Connected to EA server at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to EA server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from EA server"""
        if self.is_connected and self.socket:
            self.socket.close()
            self.is_connected = False
            logger.info("Disconnected from EA server")
    
    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message to EA server"""
        if not self.is_connected:
            raise Exception("Not connected to EA server")
        
        encoded_message = MessageProtocol.encode_message(message_type, data)
        self.socket.send(encoded_message)
    
    async def send_trade_result(self, signal_id: str, success: bool, ticket: int = None, error: str = ""):
        """Send trade execution result"""
        result_data = {
            "signal_id": signal_id,
            "success": success,
            "ticket": ticket,
            "error_message": error,
            "execution_time": datetime.utcnow().isoformat()
        }
        
        await self.send_message("TRADE_RESULT", result_data)
    
    async def send_account_status(self, balance: float, equity: float, margin: float):
        """Send account status update"""
        status_data = {
            "balance": balance,
            "equity": equity,
            "margin": margin,
            "free_margin": equity - margin,
            "margin_level": (equity / margin * 100) if margin > 0 else 0,
            "profit": equity - balance,
            "open_positions": 3  # Example
        }
        
        await self.send_message("ACCOUNT_STATUS", status_data)


# Factory functions
async def create_ea_server(host: str = "0.0.0.0", port: int = 9090) -> EAServer:
    """Create and start EA server"""
    server = EAServer(host, port)
    await server.start()
    return server


async def create_ea_client(host: str = "localhost", port: int = 9090) -> EAClient:
    """Create and connect EA client"""
    client = EAClient(host, port)
    await client.connect()
    return client
