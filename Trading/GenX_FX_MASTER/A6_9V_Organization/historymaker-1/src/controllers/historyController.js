import { HistoryModel } from '../models/historyModel.js';
import { logger } from '../utils/logger.js';
import moment from 'moment';

class HistoryController {
  async getHistory(filters = {}) {
    try {
      const { symbol, timeframe, startDate, endDate, limit } = filters;
      
      let query = {};
      
      if (symbol) {
        query.symbol = symbol.toUpperCase();
      }
      
      if (timeframe) {
        query.timeframe = timeframe;
      }
      
      if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) {
          query.timestamp.$gte = new Date(startDate);
        }
        if (endDate) {
          query.timestamp.$lte = new Date(endDate);
        }
      }
      
      const history = await HistoryModel.find(query)
        .sort({ timestamp: -1 })
        .limit(limit || 100);
      
      return history;
    } catch (error) {
      logger.error('Error in getHistory:', error);
      throw error;
    }
  }
  
  async getHistoryBySymbol(symbol, filters = {}) {
    try {
      const { timeframe, startDate, endDate, limit } = filters;
      
      let query = { symbol: symbol.toUpperCase() };
      
      if (timeframe) {
        query.timeframe = timeframe;
      }
      
      if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) {
          query.timestamp.$gte = new Date(startDate);
        }
        if (endDate) {
          query.timestamp.$lte = new Date(endDate);
        }
      }
      
      const history = await HistoryModel.find(query)
        .sort({ timestamp: -1 })
        .limit(limit || 100);
      
      return history;
    } catch (error) {
      logger.error(`Error in getHistoryBySymbol for ${symbol}:`, error);
      throw error;
    }
  }
  
  async getLatestHistory(symbol = null) {
    try {
      let query = {};
      if (symbol) {
        query.symbol = symbol.toUpperCase();
      }
      
      const latest = await HistoryModel.findOne(query)
        .sort({ timestamp: -1 });
      
      return latest;
    } catch (error) {
      logger.error('Error in getLatestHistory:', error);
      throw error;
    }
  }
  
  async getHistoryStats(filters = {}) {
    try {
      const { symbol, timeframe, startDate, endDate } = filters;
      
      let query = {};
      
      if (symbol) {
        query.symbol = symbol.toUpperCase();
      }
      
      if (timeframe) {
        query.timeframe = timeframe;
      }
      
      if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) {
          query.timestamp.$gte = new Date(startDate);
        }
        if (endDate) {
          query.timestamp.$lte = new Date(endDate);
        }
      }
      
      const stats = await HistoryModel.aggregate([
        { $match: query },
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
            firstDate: { $min: '$timestamp' },
            lastDate: { $max: '$timestamp' }
          }
        }
      ]);
      
      return stats[0] || {};
    } catch (error) {
      logger.error('Error in getHistoryStats:', error);
      throw error;
    }
  }
  
  async addHistoryEntry(entry) {
    try {
      const historyEntry = new HistoryModel({
        symbol: entry.symbol.toUpperCase(),
        timeframe: entry.timeframe,
        timestamp: new Date(entry.timestamp),
        open: entry.open,
        high: entry.high,
        low: entry.low,
        close: entry.close,
        volume: entry.volume || 0
      });
      
      const savedEntry = await historyEntry.save();
      logger.info(`Added history entry for ${entry.symbol} at ${entry.timestamp}`);
      
      return savedEntry;
    } catch (error) {
      logger.error('Error in addHistoryEntry:', error);
      throw error;
    }
  }
  
  async updateHistoryEntry(id, updates) {
    try {
      const updatedEntry = await HistoryModel.findByIdAndUpdate(
        id,
        updates,
        { new: true, runValidators: true }
      );
      
      if (!updatedEntry) {
        throw new Error('History entry not found');
      }
      
      logger.info(`Updated history entry ${id}`);
      return updatedEntry;
    } catch (error) {
      logger.error('Error in updateHistoryEntry:', error);
      throw error;
    }
  }
  
  async deleteHistoryEntry(id) {
    try {
      const deletedEntry = await HistoryModel.findByIdAndDelete(id);
      
      if (!deletedEntry) {
        throw new Error('History entry not found');
      }
      
      logger.info(`Deleted history entry ${id}`);
      return deletedEntry;
    } catch (error) {
      logger.error('Error in deleteHistoryEntry:', error);
      throw error;
    }
  }
}

export const getHistoryController = new HistoryController();