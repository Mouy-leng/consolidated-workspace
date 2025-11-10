package com.a69v.productionapp.trading.interfaces;

import java.math.BigDecimal;

/**
 * Interface for receiving market data updates
 */
public interface MarketDataListener {
    
    /**
     * Called when price data is received
     * @param symbol The trading symbol
     * @param bid The bid price
     * @param ask The ask price
     * @param timestamp The timestamp of the price update
     */
    void onPriceUpdate(String symbol, BigDecimal bid, BigDecimal ask, long timestamp);
    
    /**
     * Called when there's an error with market data
     * @param error The error message
     */
    void onMarketDataError(String error);
}