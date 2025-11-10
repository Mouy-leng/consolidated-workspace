from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import asyncio
from datetime import datetime
import logging

from ..models.schemas import (
    TradeSignal, OrderRequest, OrderResponse, PortfolioStatus, 
    OrderType, OrderStatus, SignalType
)
from ..config import settings
from ..services.trading_service import TradingService
from ..services.risk_service import RiskService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/trading", tags=["trading"])
logger = logging.getLogger(__name__)

# Initialize services
trading_service = TradingService()
risk_service = RiskService()

@router.get("/signals", response_model=List[TradeSignal])
async def get_active_signals(
    symbol: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get active trading signals
    """
    try:
        signals = await trading_service.get_active_signals(symbol)
        return signals
    except Exception as e:
        logger.error(f"Failed to get trading signals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trading signals")

@router.post("/signals", response_model=TradeSignal)
async def create_signal(
    symbol: str,
    signal_type: SignalType,
    confidence: float,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new trading signal
    """
    try:
        # Risk assessment
        risk_assessment = await risk_service.assess_signal_risk(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence
        )
        
        if not risk_assessment['approved']:
            raise HTTPException(
                status_code=400, 
                detail=f"Signal rejected by risk management: {risk_assessment['reason']}"
            )
        
        # Create signal
        signal = await trading_service.create_signal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            risk_params=risk_assessment['params']
        )
        
        return signal
        
    except Exception as e:
        logger.error(f"Failed to create signal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create signal: {str(e)}")

@router.post("/orders", response_model=OrderResponse)
async def place_order(
    order_request: OrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Place a trading order
    """
    try:
        # Risk check
        risk_check = await risk_service.check_order_risk(order_request)
        if not risk_check['approved']:
            raise HTTPException(
                status_code=400,
                detail=f"Order rejected: {risk_check['reason']}"
            )
        
        # Place order
        order = await trading_service.place_order(order_request)
        return order
        
    except Exception as e:
        logger.error(f"Failed to place order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get order details
    """
    try:
        order = await trading_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        logger.error(f"Failed to get order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order")

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an order
    """
    try:
        result = await trading_service.cancel_order(order_id)
        return {"message": "Order cancelled", "order_id": order_id, "result": result}
    except Exception as e:
        logger.error(f"Failed to cancel order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")

@router.get("/portfolio", response_model=PortfolioStatus)
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    """
    Get portfolio status
    """
    try:
        portfolio = await trading_service.get_portfolio_status()
        return portfolio
    except Exception as e:
        logger.error(f"Failed to get portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio")

@router.post("/auto-trade/start")
async def start_auto_trading(
    symbols: List[str],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Start automated trading for specified symbols
    """
    try:
        background_tasks.add_task(trading_service.start_auto_trading, symbols)
        return {"message": "Auto trading started", "symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to start auto trading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start auto trading")

@router.post("/auto-trade/stop")
async def stop_auto_trading(current_user: dict = Depends(get_current_user)):
    """
    Stop automated trading
    """
    try:
        await trading_service.stop_auto_trading()
        return {"message": "Auto trading stopped"}
    except Exception as e:
        logger.error(f"Failed to stop auto trading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop auto trading")
