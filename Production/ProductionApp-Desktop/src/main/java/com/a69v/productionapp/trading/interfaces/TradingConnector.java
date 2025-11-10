package com.a69v.productionapp.trading.interfaces;

import com.a69v.productionapp.trading.model.Account;
import com.a69v.productionapp.trading.model.Order;
import com.a69v.productionapp.trading.model.Position;

import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Main interface for trading connectors (MT4/MT5, brokers, etc.)
 */
public interface TradingConnector {
    
    /**
     * Connect to the trading platform/broker
     */
    CompletableFuture<Boolean> connect();
    
    /**
     * Disconnect from the trading platform/broker
     */
    CompletableFuture<Void> disconnect();
    
    /**
     * Check if connected
     */
    boolean isConnected();
    
    /**
     * Get account information
     */
    CompletableFuture<Account> getAccount();
    
    /**
     * Place a new order
     */
    CompletableFuture<Order> placeOrder(Order order);
    
    /**
     * Modify an existing order
     */
    CompletableFuture<Order> modifyOrder(String orderId, Order updatedOrder);
    
    /**
     * Cancel an order
     */
    CompletableFuture<Boolean> cancelOrder(String orderId);
    
    /**
     * Get all open orders
     */
    CompletableFuture<List<Order>> getOpenOrders();
    
    /**
     * Get order by ID
     */
    CompletableFuture<Order> getOrder(String orderId);
    
    /**
     * Get all positions
     */
    CompletableFuture<List<Position>> getPositions();
    
    /**
     * Close a position
     */
    CompletableFuture<Boolean> closePosition(String symbol);
    
    /**
     * Subscribe to price updates for symbols
     */
    void subscribeToMarketData(List<String> symbols, MarketDataListener listener);
    
    /**
     * Subscribe to order updates
     */
    void subscribeToOrderUpdates(OrderUpdateListener listener);
    
    /**
     * Get connector name/type
     */
    String getConnectorName();
}