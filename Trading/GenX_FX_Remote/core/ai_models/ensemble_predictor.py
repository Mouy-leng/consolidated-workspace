"""
Advanced Ensemble AI Predictor for Forex Trading
Combines multiple ML models for robust trading signal generation
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import joblib
import os
from pathlib import Path

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import xgboost as xgb
import lightgbm as lgb

from core.feature_engineering.technical_features import TechnicalFeatureEngine
from core.feature_engineering.market_microstructure import MarketMicrostructureFeatures
from core.feature_engineering.sentiment_features import SentimentFeatures
from utils.model_validation import ModelValidator

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    """
    Advanced Ensemble Predictor for Forex Trading
    
    Features:
    - Multiple ML models (RF, XGBoost, LightGBM, SVM, Neural Networks)
    - Advanced feature engineering (technical, microstructure, sentiment)
    - Time series cross-validation
    - Model confidence scoring
    - Automatic retraining
    - Performance tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_engine = TechnicalFeatureEngine()
        self.microstructure_engine = MarketMicrostructureFeatures()
        self.sentiment_engine = SentimentFeatures()
        self.validator = ModelValidator()
        
        self.model_weights = {}
        self.feature_importance = {}
        self.performance_history = {}
        self.last_retrain_time = {}
        
        # Model directory
        self.model_dir = Path("ai_models/ensemble_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_initialized = False
        logger.info("Ensemble Predictor initialized")
    
    async def initialize(self):
        """Initialize the ensemble predictor"""
        try:
            # Load existing models if available
            await self._load_models()
            
            # Initialize feature engines
            await self.feature_engine.initialize()
            await self.microstructure_engine.initialize()
            await self.sentiment_engine.initialize()
            
            self.is_initialized = True
            logger.info("Ensemble Predictor initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing ensemble predictor: {e}")
            raise
    
    async def predict(
        self,
        symbol: str,
        data: pd.DataFrame,
        multi_timeframe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Dict[str, Any]:
        """
        Generate trading prediction using ensemble of models
        
        Args:
            symbol: Currency pair
            data: Primary timeframe data
            multi_timeframe_data: Data from multiple timeframes
            
        Returns:
            Prediction dictionary with confidence, direction, and model scores
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Generate features
            features = await self._generate_features(symbol, data, multi_timeframe_data)
            
            if features is None or len(features) == 0:
                return self._get_default_prediction()
            
            # Get predictions from all models
            model_predictions = await self._get_model_predictions(symbol, features)
            
            # Calculate ensemble prediction
            ensemble_result = self._calculate_ensemble_prediction(model_predictions)
            
            # Add metadata
            ensemble_result.update({
                'symbol': symbol,
                'timestamp': datetime.now(),
                'feature_count': len(features),
                'model_count': len(model_predictions),
                'model_scores': model_predictions
            })
            
            logger.debug(f"Generated prediction for {symbol}: confidence={ensemble_result['confidence']:.3f}")
            return ensemble_result
            
        except Exception as e:
            logger.error(f"Error generating prediction for {symbol}: {e}")
            return self._get_default_prediction()
    
    async def _generate_features(
        self,
        symbol: str,
        data: pd.DataFrame,
        multi_timeframe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Optional[np.ndarray]:
        """Generate comprehensive feature set"""
        try:
            if len(data) < 50:  # Minimum data required
                return None
            
            features = []
            
            # Technical features (price action, indicators)
            technical_features = await self.feature_engine.generate_features(data)
            features.extend(technical_features)
            
            # Market microstructure features (spread, volume, volatility patterns)
            microstructure_features = await self.microstructure_engine.generate_features(data)
            features.extend(microstructure_features)
            
            # Multi-timeframe features
            if multi_timeframe_data:
                mtf_features = await self._generate_multi_timeframe_features(multi_timeframe_data)
                features.extend(mtf_features)
            
            # Sentiment features (if available)
            try:
                sentiment_features = await self.sentiment_engine.generate_features(symbol)
                features.extend(sentiment_features)
            except:
                # Sentiment features are optional
                pass
            
            # Time-based features
            time_features = self._generate_time_features(data.index[-1])
            features.extend(time_features)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error generating features for {symbol}: {e}")
            return None
    
    async def _generate_multi_timeframe_features(
        self,
        multi_timeframe_data: Dict[str, pd.DataFrame]
    ) -> List[float]:
        """Generate features from multiple timeframes"""
        features = []
        
        # Standard timeframes to analyze
        timeframes = ['M15', 'H1', 'H4', 'D1']
        
        for tf in timeframes:
            if tf in multi_timeframe_data:
                data = multi_timeframe_data[tf]
                if len(data) >= 20:
                    # Trend features
                    sma_20 = data['close'].rolling(20).mean().iloc[-1]
                    sma_50 = data['close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else sma_20
                    current_price = data['close'].iloc[-1]
                    
                    trend_strength = (current_price - sma_20) / sma_20
                    trend_consistency = 1.0 if sma_20 > sma_50 else -1.0
                    
                    # Volatility features
                    volatility = data['close'].rolling(20).std().iloc[-1] / current_price
                    
                    # Momentum features
                    roc = (current_price - data['close'].iloc[-10]) / data['close'].iloc[-10] if len(data) >= 10 else 0
                    
                    features.extend([trend_strength, trend_consistency, volatility, roc])
                else:
                    features.extend([0.0, 0.0, 0.0, 0.0])
        
        return features
    
    def _generate_time_features(self, timestamp: datetime) -> List[float]:
        """Generate time-based features"""
        features = []
        
        # Hour of day (normalized)
        hour_sin = np.sin(2 * np.pi * timestamp.hour / 24)
        hour_cos = np.cos(2 * np.pi * timestamp.hour / 24)
        features.extend([hour_sin, hour_cos])
        
        # Day of week (normalized)
        dow_sin = np.sin(2 * np.pi * timestamp.weekday() / 7)
        dow_cos = np.cos(2 * np.pi * timestamp.weekday() / 7)
        features.extend([dow_sin, dow_cos])
        
        # Market session indicators
        london_session = 1.0 if 8 <= timestamp.hour < 16 else 0.0
        ny_session = 1.0 if 13 <= timestamp.hour < 21 else 0.0
        asian_session = 1.0 if timestamp.hour < 8 or timestamp.hour >= 21 else 0.0
        overlap_session = 1.0 if 13 <= timestamp.hour < 16 else 0.0
        
        features.extend([london_session, ny_session, asian_session, overlap_session])
        
        return features
    
    async def _get_model_predictions(
        self,
        symbol: str,
        features: np.ndarray
    ) -> Dict[str, float]:
        """Get predictions from all models"""
        predictions = {}
        
        # Ensure models exist for this symbol
        if symbol not in self.models:
            await self._create_models_for_symbol(symbol)
        
        symbol_models = self.models[symbol]
        symbol_scalers = self.scalers[symbol]
        
        for model_name, model in symbol_models.items():
            try:
                # Scale features
                scaler = symbol_scalers[model_name]
                scaled_features = scaler.transform(features)
                
                # Get prediction
                if hasattr(model, 'predict_proba'):
                    # Classification models
                    proba = model.predict_proba(scaled_features)[0]
                    # Convert to direction score (-1 to 1)
                    if len(proba) >= 2:
                        direction_score = proba[1] - proba[0]  # Positive for buy, negative for sell
                    else:
                        direction_score = 0.0
                else:
                    # Regression models
                    direction_score = model.predict(scaled_features)[0]
                
                # Apply model weight
                weight = self.model_weights.get(symbol, {}).get(model_name, 1.0)
                predictions[model_name] = direction_score * weight
                
            except Exception as e:
                logger.error(f"Error getting prediction from {model_name} for {symbol}: {e}")
                predictions[model_name] = 0.0
        
        return predictions
    
    def _calculate_ensemble_prediction(self, model_predictions: Dict[str, float]) -> Dict[str, Any]:
        """Calculate final ensemble prediction"""
        if not model_predictions:
            return self._get_default_prediction()
        
        # Calculate weighted average
        predictions = list(model_predictions.values())
        weights = [abs(p) for p in predictions]  # Use absolute values as weights
        
        if sum(weights) == 0:
            return self._get_default_prediction()
        
        # Weighted average direction
        weighted_direction = sum(p * w for p, w in zip(predictions, weights)) / sum(weights)
        
        # Calculate confidence based on agreement between models
        agreement = self._calculate_model_agreement(predictions)
        base_confidence = min(abs(weighted_direction), 1.0)
        confidence = base_confidence * agreement
        
        # Determine signal strength
        signal_strength = self._calculate_signal_strength(weighted_direction, confidence)
        
        return {
            'direction': weighted_direction,
            'confidence': confidence,
            'signal_strength': signal_strength,
            'model_agreement': agreement,
            'fundamental_score': 0.5  # Placeholder for fundamental analysis
        }
    
    def _calculate_model_agreement(self, predictions: List[float]) -> float:
        """Calculate agreement between models (0.0 to 1.0)"""
        if len(predictions) < 2:
            return 0.5
        
        # Convert to buy/sell/hold signals
        signals = []
        for pred in predictions:
            if pred > 0.1:
                signals.append(1)  # Buy
            elif pred < -0.1:
                signals.append(-1)  # Sell
            else:
                signals.append(0)  # Hold
        
        # Calculate agreement
        if not signals:
            return 0.5
        
        most_common = max(set(signals), key=signals.count)
        agreement_count = signals.count(most_common)
        agreement_ratio = agreement_count / len(signals)
        
        return agreement_ratio
    
    def _calculate_signal_strength(self, direction: float, confidence: float) -> str:
        """Calculate signal strength category"""
        strength_score = abs(direction) * confidence
        
        if strength_score >= 0.8:
            return "VERY_STRONG"
        elif strength_score >= 0.6:
            return "STRONG"
        elif strength_score >= 0.4:
            return "MODERATE"
        else:
            return "WEAK"
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Return default prediction when unable to generate"""
        return {
            'direction': 0.0,
            'confidence': 0.0,
            'signal_strength': "WEAK",
            'model_agreement': 0.0,
            'fundamental_score': 0.5,
            'model_scores': {}
        }
    
    async def _create_models_for_symbol(self, symbol: str):
        """Create and initialize models for a symbol"""
        logger.info(f"Creating models for {symbol}")
        
        # Initialize model containers
        self.models[symbol] = {}
        self.scalers[symbol] = {}
        self.model_weights[symbol] = {}
        
        # Define model configurations
        model_configs = {
            'random_forest': {
                'model': RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42
                ),
                'scaler': RobustScaler()
            },
            'xgboost': {
                'model': xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                ),
                'scaler': StandardScaler()
            },
            'lightgbm': {
                'model': lgb.LGBMClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                ),
                'scaler': StandardScaler()
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                ),
                'scaler': RobustScaler()
            },
            'svm': {
                'model': SVC(
                    kernel='rbf',
                    probability=True,
                    random_state=42
                ),
                'scaler': StandardScaler()
            }
        }
        
        # Initialize models
        for model_name, config in model_configs.items():
            self.models[symbol][model_name] = config['model']
            self.scalers[symbol][model_name] = config['scaler']
            self.model_weights[symbol][model_name] = 1.0
        
        logger.info(f"Created {len(model_configs)} models for {symbol}")
    
    async def train_models(
        self,
        symbol: str,
        training_data: pd.DataFrame,
        target_column: str = 'target'
    ) -> Dict[str, Any]:
        """Train models for a specific symbol"""
        try:
            logger.info(f"Training models for {symbol}")
            
            if symbol not in self.models:
                await self._create_models_for_symbol(symbol)
            
            # Prepare training data
            X, y = await self._prepare_training_data(symbol, training_data, target_column)
            
            if len(X) < 100:  # Minimum training samples
                logger.warning(f"Insufficient training data for {symbol}: {len(X)} samples")
                return {'status': 'insufficient_data'}
            
            # Train each model
            model_scores = {}
            for model_name, model in self.models[symbol].items():
                try:
                    scaler = self.scalers[symbol][model_name]
                    
                    # Scale features
                    X_scaled = scaler.fit_transform(X)
                    
                    # Time series cross-validation
                    tscv = TimeSeriesSplit(n_splits=5)
                    cv_scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='accuracy')
                    
                    # Train on full dataset
                    model.fit(X_scaled, y)
                    
                    # Calculate model weight based on performance
                    avg_score = np.mean(cv_scores)
                    self.model_weights[symbol][model_name] = max(0.1, avg_score)
                    
                    model_scores[model_name] = {
                        'cv_mean': avg_score,
                        'cv_std': np.std(cv_scores),
                        'weight': self.model_weights[symbol][model_name]
                    }
                    
                    logger.info(f"Trained {model_name} for {symbol}: CV score = {avg_score:.3f}")
                    
                except Exception as e:
                    logger.error(f"Error training {model_name} for {symbol}: {e}")
                    model_scores[model_name] = {'error': str(e)}
            
            # Save models
            await self._save_models(symbol)
            
            # Update training history
            self.last_retrain_time[symbol] = datetime.now()
            
            return {
                'status': 'success',
                'symbol': symbol,
                'training_samples': len(X),
                'models_trained': len(model_scores),
                'model_scores': model_scores,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error training models for {symbol}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _prepare_training_data(
        self,
        symbol: str,
        data: pd.DataFrame,
        target_column: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data with features and targets"""
        
        # Generate features for each row
        features_list = []
        targets = []
        
        for i in range(50, len(data)):  # Start from index 50 to have enough history
            # Get data slice for feature generation
            data_slice = data.iloc[:i+1]
            
            # Generate features
            features = await self._generate_features(symbol, data_slice)
            
            if features is not None:
                features_list.append(features.flatten())
                targets.append(data[target_column].iloc[i])
        
        X = np.array(features_list)
        y = np.array(targets)
        
        return X, y
    
    async def _save_models(self, symbol: str):
        """Save trained models to disk"""
        try:
            symbol_dir = self.model_dir / symbol
            symbol_dir.mkdir(exist_ok=True)
            
            # Save models
            for model_name, model in self.models[symbol].items():
                model_path = symbol_dir / f"{model_name}_model.joblib"
                joblib.dump(model, model_path)
            
            # Save scalers
            for scaler_name, scaler in self.scalers[symbol].items():
                scaler_path = symbol_dir / f"{scaler_name}_scaler.joblib"
                joblib.dump(scaler, scaler_path)
            
            # Save weights and metadata
            metadata = {
                'model_weights': self.model_weights[symbol],
                'last_retrain_time': self.last_retrain_time.get(symbol),
                'feature_importance': self.feature_importance.get(symbol, {})
            }
            
            metadata_path = symbol_dir / "metadata.joblib"
            joblib.dump(metadata, metadata_path)
            
            logger.info(f"Saved models for {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving models for {symbol}: {e}")
    
    async def _load_models(self):
        """Load existing models from disk"""
        try:
            if not self.model_dir.exists():
                return
            
            for symbol_dir in self.model_dir.iterdir():
                if symbol_dir.is_dir():
                    symbol = symbol_dir.name
                    
                    # Load metadata
                    metadata_path = symbol_dir / "metadata.joblib"
                    if metadata_path.exists():
                        metadata = joblib.load(metadata_path)
                        self.model_weights[symbol] = metadata.get('model_weights', {})
                        self.last_retrain_time[symbol] = metadata.get('last_retrain_time')
                        self.feature_importance[symbol] = metadata.get('feature_importance', {})
                    
                    # Load models and scalers
                    self.models[symbol] = {}
                    self.scalers[symbol] = {}
                    
                    for model_file in symbol_dir.glob("*_model.joblib"):
                        model_name = model_file.stem.replace('_model', '')
                        try:
                            self.models[symbol][model_name] = joblib.load(model_file)
                        except Exception as e:
                            logger.error(f"Error loading model {model_name} for {symbol}: {e}")
                    
                    for scaler_file in symbol_dir.glob("*_scaler.joblib"):
                        scaler_name = scaler_file.stem.replace('_scaler', '')
                        try:
                            self.scalers[symbol][scaler_name] = joblib.load(scaler_file)
                        except Exception as e:
                            logger.error(f"Error loading scaler {scaler_name} for {symbol}: {e}")
                    
                    if self.models[symbol]:
                        logger.info(f"Loaded {len(self.models[symbol])} models for {symbol}")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    async def should_retrain(self, symbol: str) -> bool:
        """Check if models should be retrained"""
        if symbol not in self.last_retrain_time:
            return True
        
        last_retrain = self.last_retrain_time[symbol]
        if last_retrain is None:
            return True
        
        retrain_interval = timedelta(hours=self.config.get('retrain_interval_hours', 24))
        return datetime.now() - last_retrain > retrain_interval
    
    def get_model_summary(self, symbol: str) -> Dict[str, Any]:
        """Get summary of models for a symbol"""
        if symbol not in self.models:
            return {'status': 'no_models'}
        
        return {
            'symbol': symbol,
            'model_count': len(self.models[symbol]),
            'model_names': list(self.models[symbol].keys()),
            'model_weights': self.model_weights.get(symbol, {}),
            'last_retrain_time': self.last_retrain_time.get(symbol),
            'feature_importance': self.feature_importance.get(symbol, {}),
            'should_retrain': self.should_retrain(symbol)
        }