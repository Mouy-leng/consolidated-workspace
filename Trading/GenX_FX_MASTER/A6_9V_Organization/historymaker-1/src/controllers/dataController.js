import { HistoryModel } from '../models/historyModel.js';
import { logger } from '../utils/logger.js';
import fs from 'fs';
import path from 'path';

class DataController {
  async getAvailableSymbols() {
    try {
      const symbols = await HistoryModel.distinct('symbol');
      return symbols.sort();
    } catch (error) {
      logger.error('Error getting available symbols:', error);
      throw error;
    }
  }
  
  async getAvailableTimeframes() {
    try {
      const timeframes = await HistoryModel.distinct('timeframe');
      return timeframes.sort();
    } catch (error) {
      logger.error('Error getting available timeframes:', error);
      throw error;
    }
  }
  
  async getDataSummary(symbol = null, timeframe = null) {
    try {
      let query = {};
      
      if (symbol) {
        query.symbol = symbol.toUpperCase();
      }
      
      if (timeframe) {
        query.timeframe = timeframe;
      }
      
      const summary = await HistoryModel.aggregate([
        { $match: query },
        {
          $group: {
            _id: {
              symbol: '$symbol',
              timeframe: '$timeframe'
            },
            count: { $sum: 1 },
            firstDate: { $min: '$timestamp' },
            lastDate: { $max: '$timestamp' },
            avgVolume: { $avg: '$volume' }
          }
        },
        {
          $project: {
            _id: 0,
            symbol: '$_id.symbol',
            timeframe: '$_id.timeframe',
            count: 1,
            firstDate: 1,
            lastDate: 1,
            avgVolume: 1
          }
        },
        { $sort: { symbol: 1, timeframe: 1 } }
      ]);
      
      return summary;
    } catch (error) {
      logger.error('Error getting data summary:', error);
      throw error;
    }
  }
  
  async exportData(options = {}) {
    try {
      const { symbol, timeframe, startDate, endDate, format = 'csv' } = options;
      
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
      
      const data = await HistoryModel.find(query)
        .sort({ timestamp: 1 })
        .lean();
      
      if (format === 'csv') {
        return this.convertToCSV(data);
      } else if (format === 'json') {
        return data;
      } else {
        throw new Error(`Unsupported format: ${format}`);
      }
    } catch (error) {
      logger.error('Error exporting data:', error);
      throw error;
    }
  }
  
  async importData(options = {}) {
    try {
      const { data, format = 'csv', symbol, timeframe } = options;
      
      let parsedData;
      
      if (format === 'csv') {
        parsedData = this.parseCSV(data);
      } else if (format === 'json') {
        parsedData = Array.isArray(data) ? data : [data];
      } else {
        throw new Error(`Unsupported format: ${format}`);
      }
      
      const historyEntries = parsedData.map(entry => ({
        symbol: (symbol || entry.symbol).toUpperCase(),
        timeframe: timeframe || entry.timeframe,
        timestamp: new Date(entry.timestamp),
        open: parseFloat(entry.open),
        high: parseFloat(entry.high),
        low: parseFloat(entry.low),
        close: parseFloat(entry.close),
        volume: parseInt(entry.volume) || 0
      }));
      
      const result = await HistoryModel.insertMany(historyEntries);
      
      logger.info(`Imported ${result.length} history entries`);
      
      return {
        imported: result.length,
        entries: result
      };
    } catch (error) {
      logger.error('Error importing data:', error);
      throw error;
    }
  }
  
  convertToCSV(data) {
    if (!data || data.length === 0) {
      return '';
    }
    
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(entry => 
      Object.values(entry).map(value => 
        typeof value === 'string' ? `"${value}"` : value
      ).join(',')
    );
    
    return [headers, ...rows].join('\n');
  }
  
  parseCSV(csvData) {
    const lines = csvData.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    return lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
      const entry = {};
      
      headers.forEach((header, index) => {
        entry[header] = values[index];
      });
      
      return entry;
    });
  }
  
  async backupData(backupPath = null) {
    try {
      const data = await HistoryModel.find({}).lean();
      
      if (!backupPath) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        backupPath = path.join(process.cwd(), 'backups', `history_backup_${timestamp}.json`);
      }
      
      // Ensure backup directory exists
      const backupDir = path.dirname(backupPath);
      if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
      }
      
      fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
      
      logger.info(`Data backup created at: ${backupPath}`);
      
      return {
        backupPath,
        recordCount: data.length
      };
    } catch (error) {
      logger.error('Error backing up data:', error);
      throw error;
    }
  }
  
  async restoreData(backupPath) {
    try {
      if (!fs.existsSync(backupPath)) {
        throw new Error(`Backup file not found: ${backupPath}`);
      }
      
      const backupData = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
      
      // Clear existing data
      await HistoryModel.deleteMany({});
      
      // Restore data
      const result = await HistoryModel.insertMany(backupData);
      
      logger.info(`Data restored from backup: ${backupPath}`);
      
      return {
        restored: result.length,
        backupPath
      };
    } catch (error) {
      logger.error('Error restoring data:', error);
      throw error;
    }
  }
}

export const dataController = new DataController();