"""
Machine Learning Models for Trading Prediction
Advanced ML models for price prediction, sentiment analysis, and anomaly detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta
import pickle
import json
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Try to import deep learning libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Conv1D, MaxPooling1D, Flatten
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available. LSTM models will be disabled.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. XGBoost models will be disabled.")

class FeatureEngineer:
    """Feature engineering for trading data"""
    
    def __init__(self):
        self.scalers = {}
        self.logger = logging.getLogger(__name__)
    
    def create_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicator features"""
        df = data.copy()
        
        # Price-based features
        df['high_low_pct'] = (df['High'] - df['Low']) / df['Close']
        df['open_close_pct'] = (df['Close'] - df['Open']) / df['Open']
        df['close_lag1'] = df['Close'].shift(1)
        df['close_lag2'] = df['Close'].shift(2)
        df['close_lag3'] = df['Close'].shift(3)
        
        # Returns
        df['returns_1'] = df['Close'].pct_change(1)
        df['returns_2'] = df['Close'].pct_change(2)
        df['returns_5'] = df['Close'].pct_change(5)
        df['returns_10'] = df['Close'].pct_change(10)
        
        # Volatility
        df['volatility_5'] = df['returns_1'].rolling(5).std()
        df['volatility_10'] = df['returns_1'].rolling(10).std()
        df['volatility_20'] = df['returns_1'].rolling(20).std()
        
        # Moving averages
        for period in [5, 10, 20, 50, 100]:
            df[f'ma_{period}'] = df['Close'].rolling(period).mean()
            df[f'close_ma_{period}_ratio'] = df['Close'] / df[f'ma_{period}']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        df['bb_middle'] = df['Close'].rolling(bb_period).mean()
        bb_std_dev = df['Close'].rolling(bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Stochastic Oscillator
        low_14 = df['Low'].rolling(14).min()
        high_14 = df['High'].rolling(14).max()
        df['stoch_k'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()
        
        # Volume features (if available)
        if 'Volume' in df.columns:
            df['volume_ma_5'] = df['Volume'].rolling(5).mean()
            df['volume_ma_10'] = df['Volume'].rolling(10).mean()
            df['volume_ratio_5'] = df['Volume'] / df['volume_ma_5']
            df['volume_ratio_10'] = df['Volume'] / df['volume_ma_10']
            df['price_volume'] = df['Close'] * df['Volume']
        
        # Time-based features
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        # Cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def create_target_variables(self, data: pd.DataFrame, prediction_horizon: int = 1) -> pd.DataFrame:
        """Create target variables for prediction"""
        df = data.copy()
        
        # Future price targets
        df['target_price'] = df['Close'].shift(-prediction_horizon)
        df['target_return'] = df['Close'].pct_change(prediction_horizon).shift(-prediction_horizon)
        
        # Direction targets
        df['target_direction'] = np.where(df['target_return'] > 0, 1, 0)
        
        # Volatility targets
        df['target_volatility'] = df['Close'].rolling(prediction_horizon).std().shift(-prediction_horizon)
        
        # High/Low targets
        df['target_high'] = df['High'].rolling(prediction_horizon).max().shift(-prediction_horizon)
        df['target_low'] = df['Low'].rolling(prediction_horizon).min().shift(-prediction_horizon)
        
        return df
    
    def prepare_features(self, data: pd.DataFrame, target_col: str = 'target_return') -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target for ML models"""
        # Create technical features
        df = self.create_technical_features(data)
        df = self.create_target_variables(df)
        
        # Select feature columns (exclude OHLCV and target columns)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume'] + [col for col in df.columns if col.startswith('target_')]
        feature_cols = [col for col in df.columns if col not in exclude_cols and not df[col].dtype == 'object']
        
        # Remove rows with NaN values
        df_clean = df.dropna()
        
        if len(df_clean) == 0:
            raise ValueError("No valid data after feature engineering and NaN removal")
        
        X = df_clean[feature_cols]
        y = df_clean[target_col]
        
        self.logger.info(f"Features created: {len(feature_cols)} features, {len(X)} samples")
        
        return X, y

class TradingMLModels:
    """Machine Learning models for trading prediction"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.logger = logging.getLogger(__name__)
        
    def _default_config(self) -> Dict:
        """Default configuration for ML models"""
        return {
            'test_size': 0.2,
            'validation_size': 0.1,
            'random_state': 42,
            'cv_folds': 5,
            'lstm_lookback': 60,
            'lstm_epochs': 100,
            'lstm_batch_size': 32
        }
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series, model_name: str = 'rf') -> Dict:
        """Train Random Forest model"""
        self.logger.info("Training Random Forest model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['test_size'], 
            random_state=self.config['random_state'], shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.config['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Metrics
        metrics = {
            'train_mse': mean_squared_error(y_train, y_pred_train),
            'test_mse': mean_squared_error(y_test, y_pred_test),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.feature_names = list(X.columns)
        
        self.logger.info(f"Random Forest trained. Test R2: {metrics['test_r2']:.4f}")
        
        return {
            'model': model,
            'scaler': scaler,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'predictions': {
                'y_test': y_test,
                'y_pred_test': y_pred_test
            }
        }
    
    def train_xgboost(self, X: pd.DataFrame, y: pd.Series, model_name: str = 'xgb') -> Dict:
        """Train XGBoost model"""
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not available. Install with: pip install xgboost")
        
        self.logger.info("Training XGBoost model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['test_size'], 
            random_state=self.config['random_state'], shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.config['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Metrics
        metrics = {
            'train_mse': mean_squared_error(y_train, y_pred_train),
            'test_mse': mean_squared_error(y_test, y_pred_test),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.feature_names = list(X.columns)
        
        self.logger.info(f"XGBoost trained. Test R2: {metrics['test_r2']:.4f}")
        
        return {
            'model': model,
            'scaler': scaler,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'predictions': {
                'y_test': y_test,
                'y_pred_test': y_pred_test
            }
        }
    
    def train_lstm(self, data: pd.DataFrame, target_col: str = 'Close', model_name: str = 'lstm') -> Dict:
        """Train LSTM model for time series prediction"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not available. Install with: pip install tensorflow")
        
        self.logger.info("Training LSTM model...")
        
        # Prepare data for LSTM
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data[[target_col]])
        
        # Create sequences
        lookback = self.config['lstm_lookback']
        X, y = [], []
        
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Split data
        train_size = int(len(X) * (1 - self.config['test_size']))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Build model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        # Callbacks
        early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
        reduce_lr = ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-7)
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=self.config['lstm_epochs'],
            batch_size=self.config['lstm_batch_size'],
            validation_data=(X_test, y_test),
            callbacks=[early_stopping, reduce_lr],
            verbose=0
        )
        
        # Predictions
        y_pred_train = model.predict(X_train, verbose=0)
        y_pred_test = model.predict(X_test, verbose=0)
        
        # Inverse transform predictions
        y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1)).flatten()
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        y_pred_train_actual = scaler.inverse_transform(y_pred_train).flatten()
        y_pred_test_actual = scaler.inverse_transform(y_pred_test).flatten()
        
        # Metrics
        metrics = {
            'train_mse': mean_squared_error(y_train_actual, y_pred_train_actual),
            'test_mse': mean_squared_error(y_test_actual, y_pred_test_actual),
            'train_mae': mean_absolute_error(y_train_actual, y_pred_train_actual),
            'test_mae': mean_absolute_error(y_test_actual, y_pred_test_actual),
            'train_r2': r2_score(y_train_actual, y_pred_train_actual),
            'test_r2': r2_score(y_test_actual, y_pred_test_actual)
        }
        
        # Store model
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        self.logger.info(f"LSTM trained. Test R2: {metrics['test_r2']:.4f}")
        
        return {
            'model': model,
            'scaler': scaler,
            'metrics': metrics,
            'history': history.history,
            'predictions': {
                'y_test': y_test_actual,
                'y_pred_test': y_pred_test_actual
            },
            'lookback': lookback
        }
    
    def predict(self, model_name: str, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Make predictions using trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Train the model first.")
        
        model = self.models[model_name]
        scaler = self.scalers[model_name]
        
        if model_name == 'lstm':
            # Handle LSTM prediction differently
            if isinstance(X, pd.DataFrame):
                X = X.values
            if len(X.shape) == 1:
                X = X.reshape(1, -1, 1)
            elif len(X.shape) == 2:
                X = X.reshape(X.shape[0], X.shape[1], 1)
            
            predictions = model.predict(X, verbose=0)
            return scaler.inverse_transform(predictions).flatten()
        else:
            # Handle traditional ML models
            if isinstance(X, pd.DataFrame):
                X = X.values
            X_scaled = scaler.transform(X)
            return model.predict(X_scaled)
    
    def save_model(self, model_name: str, filepath: str):
        """Save trained model to disk"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model_data = {
            'model': self.models[model_name],
            'scaler': self.scalers[model_name],
            'feature_names': self.feature_names,
            'config': self.config
        }
        
        if model_name == 'lstm':
            # Save TensorFlow model separately
            self.models[model_name].save(f"{filepath}_{model_name}_model.h5")
            model_data['model'] = f"{filepath}_{model_name}_model.h5"
        
        with open(f"{filepath}_{model_name}.pkl", 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Model {model_name} saved to {filepath}")
    
    def load_model(self, model_name: str, filepath: str):
        """Load trained model from disk"""
        with open(f"{filepath}_{model_name}.pkl", 'rb') as f:
            model_data = pickle.load(f)
        
        if model_name == 'lstm' and TENSORFLOW_AVAILABLE:
            from tensorflow.keras.models import load_model
            self.models[model_name] = load_model(model_data['model'])
        else:
            self.models[model_name] = model_data['model']
        
        self.scalers[model_name] = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.config.update(model_data['config'])
        
        self.logger.info(f"Model {model_name} loaded from {filepath}")

class ModelEvaluator:
    """Evaluate and compare ML models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_predictions(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Evaluate prediction accuracy"""
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
        }
        
        # Directional accuracy
        y_true_direction = np.where(y_true > 0, 1, 0)
        y_pred_direction = np.where(y_pred > 0, 1, 0)
        directional_accuracy = np.mean(y_true_direction == y_pred_direction)
        metrics['directional_accuracy'] = directional_accuracy
        
        return metrics
    
    def compare_models(self, results: Dict[str, Dict]) -> pd.DataFrame:
        """Compare multiple model results"""
        comparison_data = []
        
        for model_name, result in results.items():
            metrics = result['metrics']
            comparison_data.append({
                'Model': model_name,
                'Test R2': metrics['test_r2'],
                'Test MSE': metrics['test_mse'],
                'Test MAE': metrics['test_mae'],
                'Train R2': metrics['train_r2'],
                'Overfit Score': metrics['train_r2'] - metrics['test_r2']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Test R2', ascending=False)
        
        return comparison_df

if __name__ == "__main__":
    print("Trading ML Models initialized!")
    print("Available models:")
    print("- Random Forest")
    if XGBOOST_AVAILABLE:
        print("- XGBoost")
    if TENSORFLOW_AVAILABLE:
        print("- LSTM Neural Network")
    print("- Feature Engineering Pipeline")
    print("- Model Evaluation Tools")