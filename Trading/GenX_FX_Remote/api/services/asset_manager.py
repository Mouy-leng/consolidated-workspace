"""
Asset Management Service for Google Sheets/Excel integration.
Provides centralized portfolio tracking, risk management, and trade logging.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import pandas as pd
import gspread
from gspread_asyncio import AsyncioGspreadClientManager
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from google.oauth2.service_account import Credentials
import json
import os
from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Trading position data structure"""
    ticket: str
    symbol: str
    type: str  # "BUY" or "SELL"
    lots: float
    open_price: float
    current_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    open_time: datetime
    current_pnl: float
    commission: float = 0.0
    swap: float = 0.0
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L"""
        if self.type == "BUY":
            return (self.current_price - self.open_price) * self.lots * 10000
        else:
            return (self.open_price - self.current_price) * self.lots * 10000


@dataclass
class ClosedTrade:
    """Closed trade data structure"""
    ticket: str
    symbol: str
    type: str
    lots: float
    open_price: float
    close_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    open_time: datetime
    close_time: datetime
    realized_pnl: float
    commission: float = 0.0
    swap: float = 0.0
    
    @property
    def duration_hours(self) -> float:
        """Calculate trade duration in hours"""
        return (self.close_time - self.open_time).total_seconds() / 3600


@dataclass
class AccountSummary:
    """Account summary data structure"""
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    total_open_positions: int
    total_unrealized_pnl: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    last_updated: datetime


@dataclass
class RiskParameters:
    """Risk management parameters"""
    max_risk_per_trade: float = 0.02  # 2% of equity
    max_daily_drawdown: float = 0.05  # 5% daily drawdown limit
    max_correlation: float = 0.7  # Maximum correlation between positions
    max_exposure_per_currency: float = 0.1  # 10% exposure per currency
    max_lot_size: float = 1.0  # Maximum lot size per trade
    max_open_positions: int = 10  # Maximum number of open positions
    instruments_to_trade: List[str] = None
    
    def __post_init__(self):
        if self.instruments_to_trade is None:
            self.instruments_to_trade = [
                "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF",
                "AUD_USD", "USD_CAD", "NZD_USD", "EUR_GBP"
            ]


class GoogleSheetsManager:
    """Google Sheets integration for asset management"""
    
    def __init__(self, credentials_path: str, spreadsheet_key: str):
        self.credentials_path = credentials_path
        self.spreadsheet_key = spreadsheet_key
        self.client_manager = None
        self.worksheet_names = {
            "dashboard": "Dashboard",
            "open_positions": "Open Positions",
            "closed_trades": "Closed Trades",
            "risk_config": "Risk Configuration",
            "performance": "Performance Analytics"
        }
        
    async def initialize(self):
        """Initialize Google Sheets client"""
        try:
            def get_creds():
                return Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
            
            self.client_manager = AsyncioGspreadClientManager(get_creds)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    async def get_spreadsheet(self):
        """Get the spreadsheet instance"""
        client = await self.client_manager.authorize()
        return await client.open_by_key(self.spreadsheet_key)
    
    async def setup_worksheets(self):
        """Create and format all required worksheets"""
        try:
            spreadsheet = await self.get_spreadsheet()
            
            # Create worksheets if they don't exist
            for sheet_name in self.worksheet_names.values():
                try:
                    await spreadsheet.worksheet(sheet_name)
                except gspread.WorksheetNotFound:
                    await spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                    logger.info(f"Created worksheet: {sheet_name}")
            
            # Format each worksheet
            await self._format_dashboard()
            await self._format_positions_sheet()
            await self._format_trades_sheet()
            await self._format_risk_config()
            await self._format_performance_sheet()
            
        except Exception as e:
            logger.error(f"Error setting up worksheets: {e}")
            raise
    
    async def _format_dashboard(self):
        """Format the dashboard worksheet"""
        spreadsheet = await self.get_spreadsheet()
        worksheet = await spreadsheet.worksheet(self.worksheet_names["dashboard"])
        
        # Headers and structure
        headers = [
            ["Account Summary", "", "", ""],
            ["Metric", "Value", "Previous", "Change"],
            ["Balance", "", "", ""],
            ["Equity", "", "", ""],
            ["Free Margin", "", "", ""],
            ["Margin Level", "", "", ""],
            ["Open Positions", "", "", ""],
            ["Unrealized P&L", "", "", ""],
            ["Daily P&L", "", "", ""],
            ["Weekly P&L", "", "", ""],
            ["Monthly P&L", "", "", ""],
            ["", "", "", ""],
            ["Risk Metrics", "", "", ""],
            ["Max Drawdown", "", "", ""],
            ["Win Rate", "", "", ""],
            ["Profit Factor", "", "", ""],
            ["", "", "", ""],
            ["Last Updated", "", "", ""]
        ]
        
        await worksheet.update("A1:D18", headers)
        
        # Format headers
        await worksheet.format("A1:D1", {
            "textFormat": {"bold": True, "fontSize": 14},
            "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.8}
        })
        
    async def _format_positions_sheet(self):
        """Format the open positions worksheet"""
        spreadsheet = await self.get_spreadsheet()
        worksheet = await spreadsheet.worksheet(self.worksheet_names["open_positions"])
        
        headers = [
            "Ticket", "Symbol", "Type", "Lots", "Open Price", "Current Price",
            "Stop Loss", "Take Profit", "Open Time", "Unrealized P&L", "Commission", "Swap"
        ]
        
        await worksheet.update("A1:L1", [headers])
        await worksheet.format("A1:L1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.8, "green": 0.2, "blue": 0.2}
        })
    
    async def _format_trades_sheet(self):
        """Format the closed trades worksheet"""
        spreadsheet = await self.get_spreadsheet()
        worksheet = await spreadsheet.worksheet(self.worksheet_names["closed_trades"])
        
        headers = [
            "Ticket", "Symbol", "Type", "Lots", "Open Price", "Close Price",
            "Stop Loss", "Take Profit", "Open Time", "Close Time", 
            "Duration (h)", "Realized P&L", "Commission", "Swap"
        ]
        
        await worksheet.update("A1:N1", [headers])
        await worksheet.format("A1:N1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.2, "green": 0.8, "blue": 0.2}
        })
    
    async def _format_risk_config(self):
        """Format the risk configuration worksheet"""
        spreadsheet = await self.get_spreadsheet()
        worksheet = await spreadsheet.worksheet(self.worksheet_names["risk_config"])
        
        config_data = [
            ["Risk Parameter", "Value", "Description"],
            ["Max Risk Per Trade", "0.02", "Maximum risk per trade (% of equity)"],
            ["Max Daily Drawdown", "0.05", "Maximum daily drawdown limit"],
            ["Max Correlation", "0.7", "Maximum correlation between positions"],
            ["Max Exposure Per Currency", "0.1", "Maximum exposure per currency"],
            ["Max Lot Size", "1.0", "Maximum lot size per trade"],
            ["Max Open Positions", "10", "Maximum number of open positions"],
            ["", "", ""],
            ["Instruments to Trade", "", ""],
            ["EUR_USD", "TRUE", "Enable EUR/USD trading"],
            ["GBP_USD", "TRUE", "Enable GBP/USD trading"],
            ["USD_JPY", "TRUE", "Enable USD/JPY trading"],
            ["USD_CHF", "TRUE", "Enable USD/CHF trading"],
            ["AUD_USD", "TRUE", "Enable AUD/USD trading"],
            ["USD_CAD", "TRUE", "Enable USD/CAD trading"],
            ["NZD_USD", "TRUE", "Enable NZD/USD trading"],
            ["EUR_GBP", "TRUE", "Enable EUR/GBP trading"]
        ]
        
        await worksheet.update("A1:C17", config_data)
        await worksheet.format("A1:C1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.2}
        })
    
    async def _format_performance_sheet(self):
        """Format the performance analytics worksheet"""
        spreadsheet = await self.get_spreadsheet()
        worksheet = await spreadsheet.worksheet(self.worksheet_names["performance"])
        
        headers = [
            ["Performance Analytics", "", "", ""],
            ["Period", "P&L", "Trades", "Win Rate"],
            ["Today", "", "", ""],
            ["This Week", "", "", ""],
            ["This Month", "", "", ""],
            ["", "", "", ""],
            ["Top Performing Pairs", "", "", ""],
            ["Symbol", "P&L", "Trades", "Win Rate"]
        ]
        
        await worksheet.update("A1:D8", headers)
        await worksheet.format("A1:D1", {
            "textFormat": {"bold": True, "fontSize": 14},
            "backgroundColor": {"red": 0.2, "green": 0.8, "blue": 0.8}
        })
    
    async def update_dashboard(self, account_summary: AccountSummary):
        """Update dashboard with current account summary"""
        try:
            spreadsheet = await self.get_spreadsheet()
            worksheet = await spreadsheet.worksheet(self.worksheet_names["dashboard"])
            
            # Update values
            updates = [
                ["B3", account_summary.balance],
                ["B4", account_summary.equity],
                ["B5", account_summary.free_margin],
                ["B6", f"{account_summary.margin_level:.2f}%"],
                ["B7", account_summary.total_open_positions],
                ["B8", account_summary.total_unrealized_pnl],
                ["B9", account_summary.daily_pnl],
                ["B10", account_summary.weekly_pnl],
                ["B11", account_summary.monthly_pnl],
                ["B14", f"{account_summary.max_drawdown:.2f}%"],
                ["B15", f"{account_summary.win_rate:.2f}%"],
                ["B16", account_summary.profit_factor],
                ["B18", account_summary.last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")]
            ]
            
            for cell, value in updates:
                await worksheet.update(cell, value)
            
            logger.info("Dashboard updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            raise
    
    async def update_positions(self, positions: List[Position]):
        """Update open positions sheet"""
        try:
            spreadsheet = await self.get_spreadsheet()
            worksheet = await spreadsheet.worksheet(self.worksheet_names["open_positions"])
            
            # Clear existing data (except headers)
            await worksheet.clear()
            
            # Re-add headers
            headers = [
                "Ticket", "Symbol", "Type", "Lots", "Open Price", "Current Price",
                "Stop Loss", "Take Profit", "Open Time", "Unrealized P&L", "Commission", "Swap"
            ]
            await worksheet.update("A1:L1", [headers])
            
            # Add position data
            if positions:
                rows = []
                for pos in positions:
                    rows.append([
                        pos.ticket,
                        pos.symbol,
                        pos.type,
                        pos.lots,
                        pos.open_price,
                        pos.current_price,
                        pos.stop_loss or "",
                        pos.take_profit or "",
                        pos.open_time.strftime("%Y-%m-%d %H:%M:%S"),
                        pos.unrealized_pnl,
                        pos.commission,
                        pos.swap
                    ])
                
                await worksheet.update(f"A2:L{len(rows) + 1}", rows)
            
            logger.info(f"Updated {len(positions)} open positions")
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
            raise
    
    async def add_closed_trade(self, trade: ClosedTrade):
        """Add a new closed trade to the sheet"""
        try:
            spreadsheet = await self.get_spreadsheet()
            worksheet = await spreadsheet.worksheet(self.worksheet_names["closed_trades"])
            
            # Get next empty row
            values = await worksheet.get_all_values()
            next_row = len(values) + 1
            
            # Add trade data
            trade_data = [
                trade.ticket,
                trade.symbol,
                trade.type,
                trade.lots,
                trade.open_price,
                trade.close_price,
                trade.stop_loss or "",
                trade.take_profit or "",
                trade.open_time.strftime("%Y-%m-%d %H:%M:%S"),
                trade.close_time.strftime("%Y-%m-%d %H:%M:%S"),
                round(trade.duration_hours, 2),
                trade.realized_pnl,
                trade.commission,
                trade.swap
            ]
            
            await worksheet.update(f"A{next_row}:N{next_row}", [trade_data])
            logger.info(f"Added closed trade: {trade.ticket}")
            
        except Exception as e:
            logger.error(f"Error adding closed trade: {e}")
            raise
    
    async def get_risk_parameters(self) -> RiskParameters:
        """Get risk parameters from the sheet"""
        try:
            spreadsheet = await self.get_spreadsheet()
            worksheet = await spreadsheet.worksheet(self.worksheet_names["risk_config"])
            
            values = await worksheet.get_all_values()
            
            # Extract risk parameters
            risk_params = RiskParameters()
            instruments = []
            
            for row in values[1:]:  # Skip header
                if len(row) >= 2:
                    param_name = row[0].strip()
                    param_value = row[1].strip()
                    
                    if param_name == "Max Risk Per Trade":
                        risk_params.max_risk_per_trade = float(param_value)
                    elif param_name == "Max Daily Drawdown":
                        risk_params.max_daily_drawdown = float(param_value)
                    elif param_name == "Max Correlation":
                        risk_params.max_correlation = float(param_value)
                    elif param_name == "Max Exposure Per Currency":
                        risk_params.max_exposure_per_currency = float(param_value)
                    elif param_name == "Max Lot Size":
                        risk_params.max_lot_size = float(param_value)
                    elif param_name == "Max Open Positions":
                        risk_params.max_open_positions = int(param_value)
                    elif "_" in param_name and param_value.upper() == "TRUE":
                        instruments.append(param_name)
            
            if instruments:
                risk_params.instruments_to_trade = instruments
            
            return risk_params
            
        except Exception as e:
            logger.error(f"Error getting risk parameters: {e}")
            return RiskParameters()  # Return defaults


class ExcelManager:
    """Excel file manager for local asset management"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Create Excel file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            workbook = openpyxl.Workbook()
            
            # Create worksheets
            workbook.create_sheet("Dashboard")
            workbook.create_sheet("Open Positions")
            workbook.create_sheet("Closed Trades")
            workbook.create_sheet("Risk Configuration")
            workbook.create_sheet("Performance Analytics")
            
            # Remove default sheet
            if "Sheet" in workbook.sheetnames:
                workbook.remove(workbook["Sheet"])
            
            workbook.save(self.file_path)
            logger.info(f"Created new Excel file: {self.file_path}")
    
    def update_dashboard(self, account_summary: AccountSummary):
        """Update dashboard in Excel file"""
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            worksheet = workbook["Dashboard"]
            
            # Clear existing content
            worksheet.delete_rows(1, worksheet.max_row)
            
            # Add headers and data
            data = [
                ["Account Summary", "", "", ""],
                ["Metric", "Value", "Previous", "Change"],
                ["Balance", account_summary.balance, "", ""],
                ["Equity", account_summary.equity, "", ""],
                ["Free Margin", account_summary.free_margin, "", ""],
                ["Margin Level", f"{account_summary.margin_level:.2f}%", "", ""],
                ["Open Positions", account_summary.total_open_positions, "", ""],
                ["Unrealized P&L", account_summary.total_unrealized_pnl, "", ""],
                ["Daily P&L", account_summary.daily_pnl, "", ""],
                ["Weekly P&L", account_summary.weekly_pnl, "", ""],
                ["Monthly P&L", account_summary.monthly_pnl, "", ""],
                ["", "", "", ""],
                ["Risk Metrics", "", "", ""],
                ["Max Drawdown", f"{account_summary.max_drawdown:.2f}%", "", ""],
                ["Win Rate", f"{account_summary.win_rate:.2f}%", "", ""],
                ["Profit Factor", account_summary.profit_factor, "", ""],
                ["", "", "", ""],
                ["Last Updated", account_summary.last_updated.strftime("%Y-%m-%d %H:%M:%S UTC"), "", ""]
            ]
            
            for row_idx, row_data in enumerate(data, 1):
                for col_idx, value in enumerate(row_data, 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    
                    # Format headers
                    if row_idx == 1:
                        cell.font = Font(bold=True, size=14)
                        cell.fill = PatternFill(start_color="3366CC", end_color="3366CC", fill_type="solid")
            
            workbook.save(self.file_path)
            logger.info("Excel dashboard updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating Excel dashboard: {e}")
            raise
    
    def update_positions(self, positions: List[Position]):
        """Update positions in Excel file"""
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            worksheet = workbook["Open Positions"]
            
            # Clear existing content
            worksheet.delete_rows(1, worksheet.max_row)
            
            # Add headers
            headers = [
                "Ticket", "Symbol", "Type", "Lots", "Open Price", "Current Price",
                "Stop Loss", "Take Profit", "Open Time", "Unrealized P&L", "Commission", "Swap"
            ]
            
            for col_idx, header in enumerate(headers, 1):
                cell = worksheet.cell(row=1, column=col_idx)
                cell.value = header
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CC3333", end_color="CC3333", fill_type="solid")
            
            # Add position data
            for row_idx, pos in enumerate(positions, 2):
                row_data = [
                    pos.ticket,
                    pos.symbol,
                    pos.type,
                    pos.lots,
                    pos.open_price,
                    pos.current_price,
                    pos.stop_loss or "",
                    pos.take_profit or "",
                    pos.open_time.strftime("%Y-%m-%d %H:%M:%S"),
                    pos.unrealized_pnl,
                    pos.commission,
                    pos.swap
                ]
                
                for col_idx, value in enumerate(row_data, 1):
                    worksheet.cell(row=row_idx, column=col_idx).value = value
            
            workbook.save(self.file_path)
            logger.info(f"Updated {len(positions)} positions in Excel")
            
        except Exception as e:
            logger.error(f"Error updating Excel positions: {e}")
            raise


class AssetManager:
    """Main asset management service"""
    
    def __init__(self, use_google_sheets: bool = True):
        self.use_google_sheets = use_google_sheets
        self.sheets_manager = None
        self.excel_manager = None
        self.risk_parameters = RiskParameters()
        
        if use_google_sheets:
            self.sheets_manager = GoogleSheetsManager(
                credentials_path=settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
                spreadsheet_key=settings.GOOGLE_SHEETS_SPREADSHEET_KEY
            )
        else:
            self.excel_manager = ExcelManager(
                file_path=settings.EXCEL_FILE_PATH or "trading_portfolio.xlsx"
            )
    
    async def initialize(self):
        """Initialize the asset manager"""
        try:
            if self.use_google_sheets and self.sheets_manager:
                await self.sheets_manager.initialize()
                await self.sheets_manager.setup_worksheets()
                self.risk_parameters = await self.sheets_manager.get_risk_parameters()
            
            logger.info("Asset manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize asset manager: {e}")
            raise
    
    async def update_portfolio(self, account_summary: AccountSummary, positions: List[Position]):
        """Update the complete portfolio"""
        try:
            if self.use_google_sheets and self.sheets_manager:
                await self.sheets_manager.update_dashboard(account_summary)
                await self.sheets_manager.update_positions(positions)
            elif self.excel_manager:
                self.excel_manager.update_dashboard(account_summary)
                self.excel_manager.update_positions(positions)
            
            logger.info("Portfolio updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
            raise
    
    async def log_trade(self, trade: ClosedTrade):
        """Log a closed trade"""
        try:
            if self.use_google_sheets and self.sheets_manager:
                await self.sheets_manager.add_closed_trade(trade)
            # For Excel, we would append to the Closed Trades sheet
            
            logger.info(f"Trade logged: {trade.ticket}")
            
        except Exception as e:
            logger.error(f"Error logging trade: {e}")
            raise
    
    def validate_trade_risk(self, signal, current_equity: float, open_positions: List[Position]) -> bool:
        """Validate if a trade meets risk parameters"""
        try:
            # Check if instrument is allowed
            if signal.instrument not in self.risk_parameters.instruments_to_trade:
                logger.warning(f"Instrument {signal.instrument} not in allowed list")
                return False
            
            # Check maximum open positions
            if len(open_positions) >= self.risk_parameters.max_open_positions:
                logger.warning("Maximum open positions reached")
                return False
            
            # Check maximum lot size
            if signal.volume > self.risk_parameters.max_lot_size:
                logger.warning(f"Volume {signal.volume} exceeds maximum lot size")
                return False
            
            # Check risk per trade
            if signal.stop_loss:
                risk_amount = abs(signal.volume * (signal.stop_loss * 10000))  # Approximate
                risk_percentage = risk_amount / current_equity
                
                if risk_percentage > self.risk_parameters.max_risk_per_trade:
                    logger.warning(f"Risk {risk_percentage:.2%} exceeds maximum risk per trade")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating trade risk: {e}")
            return False
    
    def get_risk_parameters(self) -> RiskParameters:
        """Get current risk parameters"""
        return self.risk_parameters


# Factory function
async def create_asset_manager(use_google_sheets: bool = True) -> AssetManager:
    """Create and initialize asset manager"""
    manager = AssetManager(use_google_sheets=use_google_sheets)
    await manager.initialize()
    return manager
