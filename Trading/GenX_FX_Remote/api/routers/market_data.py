from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ..models.schemas import MarketData
from ..utils.auth import get_current_user

router = APIRouter(prefix="/market-data", tags=["market-data"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[MarketData])
async def get_market_data(
    symbol: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get market data for symbols"""
    # Mock implementation for now
    return []

@router.get("/{symbol}", response_model=MarketData)
async def get_symbol_data(
    symbol: str,
    current_user: dict = Depends(get_current_user)
):
    """Get market data for a specific symbol"""
    # Mock implementation for now
    raise HTTPException(status_code=404, detail="Symbol not found")
