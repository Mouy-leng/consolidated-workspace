from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..models.schemas import SystemStatus
from ..utils.auth import get_current_user

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

@router.get("/status", response_model=SystemStatus)
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Get system status"""
    from datetime import datetime
    
    return SystemStatus(
        api_status="healthy",
        database_status="healthy",
        model_status="healthy",
        trading_enabled=True,
        last_update=datetime.now(),
        active_strategies=["ensemble_model", "pattern_recognition"]
    )

@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """Get system metrics"""
    return {
        "requests_total": 1000,
        "predictions_total": 500,
        "trades_total": 50,
        "accuracy": 0.85
    }
