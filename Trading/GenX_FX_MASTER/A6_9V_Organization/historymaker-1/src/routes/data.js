import express from 'express';
import { dataController } from '../controllers/dataController.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get available symbols
router.get('/symbols', async (req, res) => {
  try {
    const symbols = await dataController.getAvailableSymbols();
    
    res.json({
      success: true,
      data: symbols,
      count: symbols.length
    });
  } catch (error) {
    logger.error('Error fetching symbols:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch symbols',
      message: error.message
    });
  }
});

// Get available timeframes
router.get('/timeframes', async (req, res) => {
  try {
    const timeframes = await dataController.getAvailableTimeframes();
    
    res.json({
      success: true,
      data: timeframes
    });
  } catch (error) {
    logger.error('Error fetching timeframes:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch timeframes',
      message: error.message
    });
  }
});

// Get data summary
router.get('/summary', async (req, res) => {
  try {
    const { symbol, timeframe } = req.query;
    const summary = await dataController.getDataSummary(symbol, timeframe);
    
    res.json({
      success: true,
      data: summary
    });
  } catch (error) {
    logger.error('Error fetching data summary:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch data summary',
      message: error.message
    });
  }
});

// Export data
router.post('/export', async (req, res) => {
  try {
    const { symbol, timeframe, startDate, endDate, format } = req.body;
    const exportResult = await dataController.exportData({
      symbol,
      timeframe,
      startDate,
      endDate,
      format: format || 'csv'
    });
    
    res.json({
      success: true,
      data: exportResult
    });
  } catch (error) {
    logger.error('Error exporting data:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export data',
      message: error.message
    });
  }
});

// Import data
router.post('/import', async (req, res) => {
  try {
    const { data, format, symbol, timeframe } = req.body;
    const importResult = await dataController.importData({
      data,
      format: format || 'csv',
      symbol,
      timeframe
    });
    
    res.json({
      success: true,
      data: importResult
    });
  } catch (error) {
    logger.error('Error importing data:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to import data',
      message: error.message
    });
  }
});

export { router as dataRouter };