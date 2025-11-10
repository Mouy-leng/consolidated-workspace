"""
Ensemble AI Model for Forex Trading Predictions.
Combines XGBoost, LSTM, and CNN models for robust signal generation.
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import joblib
import json
import os

# ML Libraries
import xgboost as xgb
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

# Deep Learning
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Conv1D, MaxPooling1D, Flatten, Input, concatenate
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical

# Technical Analysis
import talib
from ..core.indicators.technical_indicators import TechnicalIndicators
from ..core.patterns.pattern_detector import PatternDetector

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Prediction result structure"""
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    probability_distribution: Dict[str, float]  # Probabilities for each class
    individual_predictions: Dict[str, Any]  # Predictions from individual models
    market_conditions: Dict[str, Any]  # Market state info
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class FeatureSet:
    """Feature set for model training"""
    technical_indicators: np.ndarray
    price_sequences: np.ndarray  # For LSTM
    chart_patterns: np.ndarray   # For CNN
    labels: np.ndarray
    feature_names: List[str]
    timestamps: List[datetime]


class FeatureEngineer:
    """Feature engineering for trading models"""
    
    def __init__(self):
        self.technical_indicators = TechnicalIndicators()
        self.pattern_detector = PatternDetector()
        self.scaler = StandardScaler()
        self.price_scaler = MinMaxScaler()
        
    def engineer_features(self, df: pd.DataFrame, sequence_length: int = 60) -> FeatureSet:
        """
        Engineer comprehensive features for ensemble models
        
        Args:
            df: OHLCV DataFrame with timestamp index
            sequence_length: Length of sequences for LSTM
        """
        try:
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(df)
            
            # Detect chart patterns
            patterns = self._detect_chart_patterns(df)
            
            # Create price sequences for LSTM
            sequences = self._create_price_sequences(df, sequence_length)
            
            # Generate labels (future price direction)
            labels = self._generate_labels(df)
            
            # Combine all features
            technical_features = np.column_stack([indicators, patterns])
            
            # Get feature names
            feature_names = self._get_feature_names()
            
            # Align sequences with labels and features
            min_length = min(len(technical_features), len(sequences), len(labels))
            
            return FeatureSet(
                technical_indicators=technical_features[-min_length:],
                price_sequences=sequences[-min_length:],
                chart_patterns=self._create_chart_images(df, sequence_length)[-min_length:],
                labels=labels[-min_length:],
                feature_names=feature_names,
                timestamps=df.index[-min_length:].tolist()
            )
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            raise
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate comprehensive technical indicators"""
        features = []
        
        # Price-based features
        features.extend([
            df['close'].pct_change(),  # Returns
            df['high'] / df['close'] - 1,  # High-Close ratio
            df['low'] / df['close'] - 1,   # Low-Close ratio
            df['volume'].pct_change(),     # Volume change
        ])
        
        # Moving averages
        for period in [5, 10, 20, 50, 100]:
            ma = df['close'].rolling(period).mean()
            features.append(df['close'] / ma - 1)  # Price relative to MA
        
        # Technical indicators using TA-Lib
        features.extend([
            talib.RSI(df['close'], timeperiod=14) / 100,  # Normalized RSI
            talib.MACD(df['close'])[0],  # MACD line
            talib.MACD(df['close'])[1],  # MACD signal
            talib.MACD(df['close'])[2],  # MACD histogram
            talib.BBANDS(df['close'])[0],  # Bollinger Upper
            talib.BBANDS(df['close'])[1],  # Bollinger Middle
            talib.BBANDS(df['close'])[2],  # Bollinger Lower
            talib.ATR(df['high'], df['low'], df['close']),  # ATR
            talib.CCI(df['high'], df['low'], df['close']),  # CCI
            talib.WILLR(df['high'], df['low'], df['close']),  # Williams %R
            talib.ADX(df['high'], df['low'], df['close']),  # ADX
            talib.MOM(df['close']),  # Momentum
            talib.ROC(df['close']),  # Rate of Change
        ])
        
        # Stochastic Oscillator
        stoch_k, stoch_d = talib.STOCH(df['high'], df['low'], df['close'])
        features.extend([stoch_k, stoch_d])
        
        # Volume indicators
        features.extend([
            talib.OBV(df['close'], df['volume']),
            talib.AD(df['high'], df['low'], df['close'], df['volume']),
        ])
        
        # Combine all features
        feature_matrix = np.column_stack(features)
        
        # Handle NaN values
        feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=0.0, neginf=0.0)
        
        return feature_matrix
    
    def _detect_chart_patterns(self, df: pd.DataFrame) -> np.ndarray:
        """Detect candlestick and chart patterns"""
        patterns = []
        
        # Candlestick patterns using TA-Lib
        pattern_functions = [
            talib.CDL2CROWS, talib.CDL3BLACKCROWS, talib.CDL3INSIDE,
            talib.CDL3LINESTRIKE, talib.CDL3OUTSIDE, talib.CDL3STARSINSOUTH,
            talib.CDL3WHITESOLDIERS, talib.CDLABANDONEDBABY, talib.CDLADVANCEBLOCK,
            talib.CDLBELTHOLD, talib.CDLBREAKAWAY, talib.CDLCLOSINGMARUBOZU,
            talib.CDLCONCEALBABYSWALL, talib.CDLCOUNTERATTACK, talib.CDLDARKCLOUDCOVER,
            talib.CDLDOJI, talib.CDLDOJISTAR, talib.CDLDRAGONFLYDOJI,
            talib.CDLENGULFING, talib.CDLEVENINGDOJISTAR, talib.CDLEVENINGSTAR,
            talib.CDLGAPSIDESIDEWHITE, talib.CDLGRAVESTONEDOJI, talib.CDLHAMMER,
            talib.CDLHANGINGMAN, talib.CDLHARAMI, talib.CDLHARAMICROSS,
            talib.CDLHIGHWAVE, talib.CDLHIKKAKE, talib.CDLHOMINGPIGEON,
            talib.CDLIDENTICAL3CROWS, talib.CDLINNECK, talib.CDLINVERTEDHAMMER,
            talib.CDLKICKING, talib.CDLKICKINGBYLENGTH, talib.CDLLADDERBOTTOM,
            talib.CDLLONGLEGGEDDOJI, talib.CDLLONGLINE, talib.CDLMARUBOZU,
            talib.CDLMATCHINGLOW, talib.CDLMATHOLD, talib.CDLMORNINGDOJISTAR,
            talib.CDLMORNINGSTAR, talib.CDLONNECK, talib.CDLPIERCING,
            talib.CDLRICKSHAWMAN, talib.CDLRISEFALL3METHODS, talib.CDLSEPARATINGLINES,
            talib.CDLSHOOTINGSTAR, talib.CDLSHORTLINE, talib.CDLSPINNINGTOP,
            talib.CDLSTALLEDPATTERN, talib.CDLSTICKSANDWICH, talib.CDLTAKURI,
            talib.CDLTASUKIGAP, talib.CDLTHRUSTING, talib.CDLTRISTAR,
            talib.CDLUNIQUE3RIVER, talib.CDLUPSIDEGAP2CROWS, talib.CDLXSIDEGAP3METHODS
        ]
        
        for pattern_func in pattern_functions:
            try:
                pattern = pattern_func(df['open'], df['high'], df['low'], df['close'])
                patterns.append(pattern)
            except:
                # Some patterns might fail, add zeros
                patterns.append(np.zeros(len(df)))
        
        # Combine all patterns
        pattern_matrix = np.column_stack(patterns)
        
        # Normalize patterns (-1, 0, 1) to (0, 0.5, 1)
        pattern_matrix = (pattern_matrix + 1) / 2
        
        return pattern_matrix
    
    def _create_price_sequences(self, df: pd.DataFrame, sequence_length: int) -> np.ndarray:
        """Create price sequences for LSTM model"""
        # Use OHLCV data
        price_data = df[['open', 'high', 'low', 'close', 'volume']].values
        
        # Normalize the data
        price_data_scaled = self.price_scaler.fit_transform(price_data)
        
        sequences = []
        for i in range(sequence_length, len(price_data_scaled)):
            sequences.append(price_data_scaled[i-sequence_length:i])
        
        return np.array(sequences)
    
    def _create_chart_images(self, df: pd.DataFrame, sequence_length: int) -> np.ndarray:
        """Create chart-like images for CNN model"""
        # Create technical indicator plots as "images"
        images = []
        
        # Calculate indicators for imaging
        rsi = talib.RSI(df['close'], timeperiod=14)
        macd_line, macd_signal, macd_hist = talib.MACD(df['close'])
        bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'])
        
        for i in range(sequence_length, len(df)):
            # Create a "chart image" using multiple indicators
            window_data = df.iloc[i-sequence_length:i]
            
            # Normalize price data to 0-1 range for the window
            price_norm = (window_data['close'] - window_data['close'].min()) / \
                        (window_data['close'].max() - window_data['close'].min() + 1e-8)
            
            # Create multi-channel "image"
            channels = [
                price_norm.values,
                rsi[i-sequence_length:i].fillna(0.5),
                macd_line[i-sequence_length:i].fillna(0),
                macd_hist[i-sequence_length:i].fillna(0)
            ]
            
            # Stack channels to create a 2D image-like structure
            image = np.column_stack(channels)
            images.append(image)
        
        return np.array(images)
    
    def _generate_labels(self, df: pd.DataFrame, prediction_horizon: int = 5) -> np.ndarray:
        """Generate labels for classification (price direction)"""
        # Calculate future returns
        future_returns = df['close'].shift(-prediction_horizon) / df['close'] - 1
        
        # Create classification labels
        labels = np.zeros(len(future_returns))
        labels[future_returns > 0.001] = 2  # BUY (significant up move)
        labels[future_returns < -0.001] = 0  # SELL (significant down move)
        labels[(future_returns >= -0.001) & (future_returns <= 0.001)] = 1  # HOLD
        
        return labels[:-prediction_horizon]  # Remove last N values (no future data)
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretability"""
        names = []
        
        # Price features
        names.extend(['returns', 'high_close_ratio', 'low_close_ratio', 'volume_change'])
        
        # Moving averages
        for period in [5, 10, 20, 50, 100]:
            names.append(f'price_ma_{period}_ratio')
        
        # Technical indicators
        names.extend([
            'rsi', 'macd_line', 'macd_signal', 'macd_hist',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'cci',
            'willr', 'adx', 'momentum', 'roc', 'stoch_k', 'stoch_d',
            'obv', 'ad'
        ])
        
        # Candlestick patterns (simplified names)
        pattern_names = [f'pattern_{i}' for i in range(61)]  # Number of TA-Lib patterns
        names.extend(pattern_names)
        
        return names


class XGBoostModel:
    """XGBoost model for structured data prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train XGBoost model"""
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='mlogloss',
                early_stopping_rounds=20
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
            
            self.is_trained = True
            
            # Evaluate model
            train_score = self.model.score(X_train, y_train)
            val_score = self.model.score(X_val, y_val)
            
            logger.info(f"XGBoost trained - Train: {train_score:.3f}, Val: {val_score:.3f}")
            
            return {
                "train_accuracy": train_score,
                "val_accuracy": val_score,
                "feature_importance": dict(zip(
                    range(X.shape[1]), 
                    self.model.feature_importances_
                ))
            }
            
        except Exception as e:
            logger.error(f"Error training XGBoost model: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[int, np.ndarray]:
        """Predict using XGBoost model"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        return prediction, probabilities
    
    def save(self, path: str):
        """Save model to disk"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, path)
    
    def load(self, path: str):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.is_trained = True


class LSTMModel:
    """LSTM model for time series prediction"""
    
    def __init__(self, sequence_length: int = 60, n_features: int = 5):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        
    def build_model(self) -> Model:
        """Build LSTM architecture"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, self.n_features)),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(3, activation='softmax')  # 3 classes: SELL, HOLD, BUY
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train LSTM model"""
        try:
            # Convert labels to categorical
            y_categorical = to_categorical(y, num_classes=3)
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y_categorical[:split_idx], y_categorical[split_idx:]
            
            # Build model
            self.model = self.build_model()
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(patience=5, factor=0.5)
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                batch_size=32,
                epochs=100,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=0
            )
            
            self.is_trained = True
            
            # Evaluate
            train_loss, train_acc = self.model.evaluate(X_train, y_train, verbose=0)
            val_loss, val_acc = self.model.evaluate(X_val, y_val, verbose=0)
            
            logger.info(f"LSTM trained - Train: {train_acc:.3f}, Val: {val_acc:.3f}")
            
            return {
                "train_accuracy": train_acc,
                "val_accuracy": val_acc,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "history": history.history
            }
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[int, np.ndarray]:
        """Predict using LSTM model"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        probabilities = self.model.predict(X[-1:], verbose=0)[0]
        prediction = np.argmax(probabilities)
        
        return prediction, probabilities
    
    def save(self, path: str):
        """Save model to disk"""
        if self.is_trained:
            self.model.save(path)
    
    def load(self, path: str):
        """Load model from disk"""
        self.model = load_model(path)
        self.is_trained = True


class CNNModel:
    """CNN model for chart pattern recognition"""
    
    def __init__(self, sequence_length: int = 60, n_channels: int = 4):
        self.sequence_length = sequence_length
        self.n_channels = n_channels
        self.model = None
        self.is_trained = False
    
    def build_model(self) -> Model:
        """Build CNN architecture"""
        model = Sequential([
            Conv1D(filters=64, kernel_size=3, activation='relu', 
                   input_shape=(self.sequence_length, self.n_channels)),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=32, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=16, kernel_size=3, activation='relu'),
            Flatten(),
            Dense(50, activation='relu'),
            Dropout(0.3),
            Dense(25, activation='relu'),
            Dense(3, activation='softmax')  # 3 classes: SELL, HOLD, BUY
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train CNN model"""
        try:
            # Convert labels to categorical
            y_categorical = to_categorical(y, num_classes=3)
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y_categorical[:split_idx], y_categorical[split_idx:]
            
            # Build model
            self.model = self.build_model()
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(patience=5, factor=0.5)
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                batch_size=32,
                epochs=100,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=0
            )
            
            self.is_trained = True
            
            # Evaluate
            train_loss, train_acc = self.model.evaluate(X_train, y_train, verbose=0)
            val_loss, val_acc = self.model.evaluate(X_val, y_val, verbose=0)
            
            logger.info(f"CNN trained - Train: {train_acc:.3f}, Val: {val_acc:.3f}")
            
            return {
                "train_accuracy": train_acc,
                "val_accuracy": val_acc,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "history": history.history
            }
            
        except Exception as e:
            logger.error(f"Error training CNN model: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[int, np.ndarray]:
        """Predict using CNN model"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        probabilities = self.model.predict(X[-1:], verbose=0)[0]
        prediction = np.argmax(probabilities)
        
        return prediction, probabilities
    
    def save(self, path: str):
        """Save model to disk"""
        if self.is_trained:
            self.model.save(path)
    
    def load(self, path: str):
        """Load model from disk"""
        self.model = load_model(path)
        self.is_trained = True


class EnsemblePredictor:
    """Ensemble predictor combining XGBoost, LSTM, and CNN"""
    
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.feature_engineer = FeatureEngineer()
        self.xgb_model = XGBoostModel()
        self.lstm_model = LSTMModel(sequence_length)
        self.cnn_model = CNNModel(sequence_length)
        self.meta_learner = LogisticRegression(random_state=42)
        self.is_trained = False
        self.class_names = ["SELL", "HOLD", "BUY"]
        
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train the ensemble model"""
        try:
            logger.info("Starting ensemble model training...")
            
            # Engineer features
            features = self.feature_engineer.engineer_features(df, self.sequence_length)
            
            # Train individual models
            xgb_results = self.xgb_model.train(features.technical_indicators, features.labels)
            lstm_results = self.lstm_model.train(features.price_sequences, features.labels)
            cnn_results = self.cnn_model.train(features.chart_patterns, features.labels)
            
            # Create meta-features for meta-learner
            meta_features = self._create_meta_features(features)
            
            # Train meta-learner
            self.meta_learner.fit(meta_features, features.labels)
            
            self.is_trained = True
            
            logger.info("Ensemble model training completed successfully")
            
            return {
                "xgb_results": xgb_results,
                "lstm_results": lstm_results,
                "cnn_results": cnn_results,
                "meta_learner_score": self.meta_learner.score(meta_features, features.labels)
            }
            
        except Exception as e:
            logger.error(f"Error training ensemble model: {e}")
            raise
    
    def _create_meta_features(self, features: FeatureSet) -> np.ndarray:
        """Create meta-features from individual model predictions"""
        meta_features = []
        
        for i in range(len(features.labels)):
            # Get individual predictions
            xgb_pred, xgb_proba = self.xgb_model.predict(features.technical_indicators[i:i+1])
            lstm_pred, lstm_proba = self.lstm_model.predict(features.price_sequences[i:i+1])
            cnn_pred, cnn_proba = self.cnn_model.predict(features.chart_patterns[i:i+1])
            
            # Combine predictions and probabilities as meta-features
            meta_feature = np.concatenate([
                [xgb_pred, lstm_pred, cnn_pred],  # Class predictions
                xgb_proba, lstm_proba, cnn_proba  # Probability distributions
            ])
            
            meta_features.append(meta_feature)
        
        return np.array(meta_features)
    
    def predict(self, df: pd.DataFrame) -> PredictionResult:
        """Make ensemble prediction"""
        if not self.is_trained:
            raise ValueError("Ensemble model not trained")
        
        try:
            # Engineer features for the latest data
            features = self.feature_engineer.engineer_features(df, self.sequence_length)
            
            # Get individual model predictions
            xgb_pred, xgb_proba = self.xgb_model.predict(features.technical_indicators[-1:])
            lstm_pred, lstm_proba = self.lstm_model.predict(features.price_sequences[-1:])
            cnn_pred, cnn_proba = self.cnn_model.predict(features.chart_patterns[-1:])
            
            # Create meta-features
            meta_feature = np.concatenate([
                [xgb_pred, lstm_pred, cnn_pred],
                xgb_proba, lstm_proba, cnn_proba
            ]).reshape(1, -1)
            
            # Get ensemble prediction
            ensemble_pred = self.meta_learner.predict(meta_feature)[0]
            ensemble_proba = self.meta_learner.predict_proba(meta_feature)[0]
            
            # Calculate confidence as max probability
            confidence = np.max(ensemble_proba)
            
            # Create probability distribution
            prob_dist = {
                "SELL": ensemble_proba[0],
                "HOLD": ensemble_proba[1],
                "BUY": ensemble_proba[2]
            }
            
            # Individual predictions for transparency
            individual_preds = {
                "xgb": {"prediction": self.class_names[xgb_pred], "probabilities": xgb_proba.tolist()},
                "lstm": {"prediction": self.class_names[lstm_pred], "probabilities": lstm_proba.tolist()},
                "cnn": {"prediction": self.class_names[cnn_pred], "probabilities": cnn_proba.tolist()}
            }
            
            # Market conditions
            latest_data = df.iloc[-1]
            market_conditions = {
                "current_price": latest_data['close'],
                "volume": latest_data['volume'],
                "rsi": talib.RSI(df['close'], timeperiod=14).iloc[-1],
                "volatility": df['close'].pct_change().rolling(20).std().iloc[-1]
            }
            
            return PredictionResult(
                signal=self.class_names[ensemble_pred],
                confidence=confidence,
                probability_distribution=prob_dist,
                individual_predictions=individual_preds,
                market_conditions=market_conditions,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error making ensemble prediction: {e}")
            raise
    
    def save_models(self, model_dir: str):
        """Save all models to directory"""
        os.makedirs(model_dir, exist_ok=True)
        
        self.xgb_model.save(os.path.join(model_dir, "xgb_model.pkl"))
        self.lstm_model.save(os.path.join(model_dir, "lstm_model.h5"))
        self.cnn_model.save(os.path.join(model_dir, "cnn_model.h5"))
        joblib.dump(self.meta_learner, os.path.join(model_dir, "meta_learner.pkl"))
        
        # Save feature engineer scaler
        joblib.dump(self.feature_engineer.scaler, os.path.join(model_dir, "feature_scaler.pkl"))
        joblib.dump(self.feature_engineer.price_scaler, os.path.join(model_dir, "price_scaler.pkl"))
        
        logger.info(f"Models saved to {model_dir}")
    
    def load_models(self, model_dir: str):
        """Load all models from directory"""
        self.xgb_model.load(os.path.join(model_dir, "xgb_model.pkl"))
        self.lstm_model.load(os.path.join(model_dir, "lstm_model.h5"))
        self.cnn_model.load(os.path.join(model_dir, "cnn_model.h5"))
        self.meta_learner = joblib.load(os.path.join(model_dir, "meta_learner.pkl"))
        
        # Load feature engineer scalers
        self.feature_engineer.scaler = joblib.load(os.path.join(model_dir, "feature_scaler.pkl"))
        self.feature_engineer.price_scaler = joblib.load(os.path.join(model_dir, "price_scaler.pkl"))
        
        self.is_trained = True
        logger.info(f"Models loaded from {model_dir}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from XGBoost model"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        feature_names = self.feature_engineer._get_feature_names()
        importance = self.xgb_model.model.feature_importances_
        
        return dict(zip(feature_names, importance))


# Factory function
def create_ensemble_predictor(sequence_length: int = 60) -> EnsemblePredictor:
    """Create ensemble predictor instance"""
    return EnsemblePredictor(sequence_length=sequence_length)
