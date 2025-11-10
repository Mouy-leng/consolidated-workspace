from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import joblib
import asyncio
from datetime import datetime
import logging

from ..models.schemas import PredictionRequest, PredictionResponse, SignalType, ModelMetrics
from ..config import settings
from ..services.ml_service import MLService
from ..services.data_service import DataService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)

# Initialize services
ml_service = MLService()
data_service = DataService()

@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered market prediction for a given symbol
    """
    try:
        # Get real-time market data
        market_data = await data_service.get_realtime_data(request.symbol)
        if not market_data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol}")
        
        # Generate prediction
        prediction_result = await ml_service.predict(
            symbol=request.symbol,
            market_data=market_data,
            use_ensemble=request.use_ensemble
        )
        
        # Log prediction for future model training
        background_tasks.add_task(
            ml_service.log_prediction,
            request.symbol,
            prediction_result
        )
        
        return PredictionResponse(
            symbol=request.symbol,
            prediction=SignalType(prediction_result['signal']),
            confidence=prediction_result['confidence'],
            timestamp=datetime.now(),
            features_used=prediction_result['features'],
            model_version=prediction_result['model_version']
        )
        
    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/batch/{symbols}")
async def batch_predictions(
    symbols: str,
    timeframe: str = "1h",
    use_ensemble: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate predictions for multiple symbols
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    tasks = []
    for symbol in symbol_list:
        task = create_prediction(
            PredictionRequest(
                symbol=symbol,
                timeframe=timeframe,
                use_ensemble=use_ensemble
            ),
            BackgroundTasks(),
            current_user
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    predictions = []
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append({"symbol": symbol_list[i], "error": str(result)})
        else:
            predictions.append(result)
    
    return {
        "predictions": predictions,
        "errors": errors,
        "total_processed": len(symbol_list)
    }

@router.get("/model/metrics", response_model=ModelMetrics)
async def get_model_metrics(current_user: dict = Depends(get_current_user)):
    """
    Get current model performance metrics
    """
    try:
        metrics = await ml_service.get_model_metrics()
        return ModelMetrics(**metrics)
    except Exception as e:
        logger.error(f"Failed to get model metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model metrics")

@router.post("/model/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    symbols: List[str] = ["BTCUSDT", "ETHUSDT"],
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger model retraining with latest data
    """
    try:
        background_tasks.add_task(ml_service.retrain_model, symbols)
        return {"message": "Model retraining started", "symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to start model retraining: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start model retraining")
