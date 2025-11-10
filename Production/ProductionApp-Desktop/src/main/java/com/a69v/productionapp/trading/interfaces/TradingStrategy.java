package com.a69v.productionapp.trading.interfaces;

import com.a69v.productionapp.trading.model.Order;
import java.math.BigDecimal;
import java.util.List;

/**
 * Interface for trading strategies
 */
public interface TradingStrategy {
    
    /**
     * Get the strategy name
     */
    String getName();
    
    /**
     * Get symbols this strategy trades
     */
    List<String> getSymbols();
    
    /**
     * Initialize the strategy with configuration
     */
    void initialize();
    
    /**
     * Process price update and generate trading signals
     * @param symbol The symbol
     * @param bid The bid price
     * @param ask The ask price
     * @param timestamp The timestamp
     * @return List of orders to place (empty if no signals)
     */
    List<Order> onPriceUpdate(String symbol, BigDecimal bid, BigDecimal ask, long timestamp);
    
    /**
     * Check if strategy is enabled
     */
    boolean isEnabled();
    
    /**
     * Shutdown the strategy
     */
    void shutdown();
}