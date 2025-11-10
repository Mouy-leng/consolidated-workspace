import express from 'express';
import { getHistoryController } from '../controllers/historyController.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get trading history
router.get('/', async (req, res) => {
  try {
    const { symbol, timeframe, startDate, endDate, limit } = req.query;
    const history = await getHistoryController.getHistory({
      symbol,
      timeframe,
      startDate,
      endDate,
      limit: parseInt(limit) || 100
    });
    
    res.json({
      success: true,
      data: history,
      count: history.length
    });
  } catch (error) {
    logger.error('Error fetching history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch history data',
      message: error.message
    });
  }
});

// Get history by symbol
router.get('/symbol/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { timeframe, startDate, endDate, limit } = req.query;
    
    const history = await getHistoryController.getHistoryBySymbol(symbol, {
      timeframe,
      startDate,
      endDate,
      limit: parseInt(limit) || 100
    });
    
    res.json({
      success: true,
      data: history,
      symbol,
      count: history.length
    });
  } catch (error) {
    logger.error(`Error fetching history for symbol ${req.params.symbol}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch history data',
      message: error.message
    });
  }
});

// Get latest history entry
router.get('/latest', async (req, res) => {
  try {
    const { symbol } = req.query;
    const latest = await getHistoryController.getLatestHistory(symbol);
    
    res.json({
      success: true,
      data: latest
    });
  } catch (error) {
    logger.error('Error fetching latest history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch latest history',
      message: error.message
    });
  }
});

// Get history statistics
router.get('/stats', async (req, res) => {
  try {
    const { symbol, timeframe, startDate, endDate } = req.query;
    const stats = await getHistoryController.getHistoryStats({
      symbol,
      timeframe,
      startDate,
      endDate
    });
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    logger.error('Error fetching history stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch history statistics',
      message: error.message
    });
  }
});

export { router as historyRouter };