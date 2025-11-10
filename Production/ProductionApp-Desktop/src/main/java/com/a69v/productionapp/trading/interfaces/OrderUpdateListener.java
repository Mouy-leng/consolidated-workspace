package com.a69v.productionapp.trading.interfaces;

import com.a69v.productionapp.trading.model.Order;

/**
 * Interface for receiving order update notifications
 */
public interface OrderUpdateListener {
    
    /**
     * Called when an order status changes
     * @param order The updated order
     */
    void onOrderUpdate(Order order);
    
    /**
     * Called when an order is filled
     * @param order The filled order
     */
    void onOrderFilled(Order order);
    
    /**
     * Called when an order is cancelled
     * @param order The cancelled order
     */
    void onOrderCancelled(Order order);
    
    /**
     * Called when there's an error with an order
     * @param orderId The order ID
     * @param error The error message
     */
    void onOrderError(String orderId, String error);
}