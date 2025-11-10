import mongoose from 'mongoose';

const historySchema = new mongoose.Schema({
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  timeframe: {
    type: String,
    required: true,
    enum: ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'],
    index: true
  },
  timestamp: {
    type: Date,
    required: true,
    index: true
  },
  open: {
    type: Number,
    required: true
  },
  high: {
    type: Number,
    required: true
  },
  low: {
    type: Number,
    required: true
  },
  close: {
    type: Number,
    required: true
  },
  volume: {
    type: Number,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  collection: 'trading_history'
});

// Compound index for efficient queries
historySchema.index({ symbol: 1, timeframe: 1, timestamp: -1 });

// Index for date range queries
historySchema.index({ timestamp: -1 });

// Virtual for price range
historySchema.virtual('priceRange').get(function() {
  return this.high - this.low;
});

// Virtual for body size
historySchema.virtual('bodySize').get(function() {
  return Math.abs(this.close - this.open);
});

// Virtual for is bullish
historySchema.virtual('isBullish').get(function() {
  return this.close > this.open;
});

// Virtual for is bearish
historySchema.virtual('isBearish').get(function() {
  return this.close < this.open;
});

// Virtual for is doji
historySchema.virtual('isDoji').get(function() {
  return Math.abs(this.close - this.open) < (this.high - this.low) * 0.1;
});

// Pre-save middleware to validate data
historySchema.pre('save', function(next) {
  // Validate OHLC relationships
  if (this.high < Math.max(this.open, this.close)) {
    return next(new Error('High price must be greater than or equal to open and close'));
  }
  
  if (this.low > Math.min(this.open, this.close)) {
    return next(new Error('Low price must be less than or equal to open and close'));
  }
  
  // Validate volume
  if (this.volume < 0) {
    return next(new Error('Volume cannot be negative'));
  }
  
  next();
});

// Static method to get latest entry for a symbol
historySchema.statics.getLatestBySymbol = function(symbol, timeframe = null) {
  const query = { symbol: symbol.toUpperCase() };
  if (timeframe) {
    query.timeframe = timeframe;
  }
  
  return this.findOne(query).sort({ timestamp: -1 });
};

// Static method to get entries within date range
historySchema.statics.getByDateRange = function(symbol, timeframe, startDate, endDate) {
  const query = {
    symbol: symbol.toUpperCase(),
    timestamp: {
      $gte: new Date(startDate),
      $lte: new Date(endDate)
    }
  };
  
  if (timeframe) {
    query.timeframe = timeframe;
  }
  
  return this.find(query).sort({ timestamp: 1 });
};

// Static method to get statistics for a symbol
historySchema.statics.getStats = function(symbol, timeframe = null, startDate = null, endDate = null) {
  const match = { symbol: symbol.toUpperCase() };
  
  if (timeframe) {
    match.timeframe = timeframe;
  }
  
  if (startDate || endDate) {
    match.timestamp = {};
    if (startDate) {
      match.timestamp.$gte = new Date(startDate);
    }
    if (endDate) {
      match.timestamp.$lte = new Date(endDate);
    }
  }
  
  return this.aggregate([
    { $match: match },
    {
      $group: {
        _id: null,
        count: { $sum: 1 },
        avgOpen: { $avg: '$open' },
        avgHigh: { $avg: '$high' },
        avgLow: { $avg: '$low' },
        avgClose: { $avg: '$close' },
        avgVolume: { $avg: '$volume' },
        minOpen: { $min: '$open' },
        maxOpen: { $max: '$open' },
        minClose: { $min: '$close' },
        maxClose: { $max: '$close' },
        minLow: { $min: '$low' },
        maxHigh: { $max: '$high' },
        firstDate: { $min: '$timestamp' },
        lastDate: { $max: '$timestamp' }
      }
    }
  ]);
};

// Instance method to calculate technical indicators
historySchema.methods.calculateRSI = function(period = 14) {
  // This would need to be implemented with historical data
  // For now, return null as it requires multiple data points
  return null;
};

// Instance method to get price change
historySchema.methods.getPriceChange = function() {
  return this.close - this.open;
};

// Instance method to get price change percentage
historySchema.methods.getPriceChangePercent = function() {
  return ((this.close - this.open) / this.open) * 100;
};

export const HistoryModel = mongoose.model('History', historySchema);