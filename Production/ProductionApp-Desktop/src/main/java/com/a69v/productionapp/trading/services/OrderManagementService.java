package com.a69v.productionapp.trading.services;

import com.a69v.productionapp.trading.interfaces.OrderUpdateListener;
import com.a69v.productionapp.trading.interfaces.TradingConnector;
import com.a69v.productionapp.trading.model.Order;
import com.a69v.productionapp.trading.model.Position;
import com.a69v.productionapp.trading.enums.OrderStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

/**
 * Order Management System that handles order placement, tracking, and lifecycle management
 */
public class OrderManagementService implements OrderUpdateListener {
    private static final Logger logger = LoggerFactory.getLogger(OrderManagementService.class);
    
    private final TradingConnector connector;
    private final Map<String, Order> activeOrders;
    private final Map<String, Consumer<Order>> orderCallbacks;
    private final ScheduledExecutorService scheduler;
    
    // Event listeners
    private Consumer<Order> onOrderFilled;
    private Consumer<Order> onOrderCancelled;
    private Consumer<String> onOrderError;
    
    public OrderManagementService(TradingConnector connector) {
        this.connector = connector;
        this.activeOrders = new ConcurrentHashMap<>();
        this.orderCallbacks = new ConcurrentHashMap<>();
        this.scheduler = Executors.newScheduledThreadPool(2);
        
        // Subscribe to order updates from the connector
        connector.subscribeToOrderUpdates(this);
        
        // Start periodic order status updates
        startOrderStatusUpdates();
    }
    
    /**
     * Place a new order
     */
    public CompletableFuture<Order> placeOrder(Order order) {
        return placeOrder(order, null);
    }
    
    /**
     * Place a new order with callback
     */
    public CompletableFuture<Order> placeOrder(Order order, Consumer<Order> callback) {
        logger.info("Placing order: {}", order);
        
        return connector.placeOrder(order)
            .whenComplete((result, throwable) -> {
                if (throwable == null && result != null) {
                    activeOrders.put(result.getOrderId(), result);
                    if (callback != null) {
                        orderCallbacks.put(result.getOrderId(), callback);
                    }
                    logger.info("Order placed successfully: {}", result.getOrderId());
                } else {
                    logger.error("Failed to place order: {}", 
                        throwable != null ? throwable.getMessage() : "Unknown error");
                    if (onOrderError != null) {
                        onOrderError.accept("Failed to place order: " + 
                            (throwable != null ? throwable.getMessage() : "Unknown error"));
                    }
                }
            });
    }
    
    /**
     * Cancel an existing order
     */
    public CompletableFuture<Boolean> cancelOrder(String orderId) {
        logger.info("Cancelling order: {}", orderId);
        
        return connector.cancelOrder(orderId)
            .whenComplete((result, throwable) -> {
                if (throwable == null && result) {
                    Order order = activeOrders.get(orderId);
                    if (order != null) {
                        order.setStatus(OrderStatus.CANCELLED);
                        logger.info("Order cancelled successfully: {}", orderId);
                    }
                } else {
                    logger.error("Failed to cancel order {}: {}", orderId,
                        throwable != null ? throwable.getMessage() : "Unknown error");
                }
            });
    }
    
    /**
     * Modify an existing order
     */
    public CompletableFuture<Order> modifyOrder(String orderId, Order updatedOrder) {
        logger.info("Modifying order: {}", orderId);
        
        return connector.modifyOrder(orderId, updatedOrder)
            .whenComplete((result, throwable) -> {
                if (throwable == null && result != null) {
                    activeOrders.put(result.getOrderId(), result);
                    logger.info("Order modified successfully: {}", result.getOrderId());
                } else {
                    logger.error("Failed to modify order {}: {}", orderId,
                        throwable != null ? throwable.getMessage() : "Unknown error");
                }
            });
    }
    
    /**
     * Get all active orders
     */
    public Map<String, Order> getActiveOrders() {
        return new ConcurrentHashMap<>(activeOrders);
    }
    
    /**
     * Get order by ID
     */
    public Order getOrder(String orderId) {
        return activeOrders.get(orderId);
    }
    
    /**
     * Close all positions for a symbol
     */
    public CompletableFuture<Boolean> closeAllPositions(String symbol) {
        logger.info("Closing all positions for: {}", symbol);
        return connector.closePosition(symbol);
    }
    
    /**
     * Get all current positions
     */
    public CompletableFuture<List<Position>> getPositions() {
        return connector.getPositions();
    }
    
    /**
     * Cancel all open orders
     */
    public CompletableFuture<Void> cancelAllOrders() {
        logger.info("Cancelling all open orders");
        
        List<CompletableFuture<Boolean>> cancelFutures = activeOrders.keySet().stream()
            .map(this::cancelOrder)
            .toList();
            
        return CompletableFuture.allOf(cancelFutures.toArray(new CompletableFuture[0]));
    }
    
    /**
     * Emergency stop - cancel all orders and close all positions
     */
    public CompletableFuture<Void> emergencyStop() {
        logger.warn("EMERGENCY STOP - Closing all positions and cancelling all orders");
        
        CompletableFuture<Void> cancelOrders = cancelAllOrders();
        
        CompletableFuture<Void> closePositions = getPositions()
            .thenCompose(positions -> {
                List<CompletableFuture<Boolean>> closeFutures = positions.stream()
                    .map(position -> closeAllPositions(position.getSymbol()))
                    .toList();
                return CompletableFuture.allOf(closeFutures.toArray(new CompletableFuture[0]));
            });
            
        return CompletableFuture.allOf(cancelOrders, closePositions);
    }
    
    /**
     * Start periodic order status updates
     */
    private void startOrderStatusUpdates() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                updateOrderStatuses();
            } catch (Exception e) {
                logger.error("Error updating order statuses: {}", e.getMessage());
            }
        }, 5, 5, TimeUnit.SECONDS);
    }
    
    /**
     * Update order statuses from the connector
     */
    private void updateOrderStatuses() {
        if (activeOrders.isEmpty()) {
            return;
        }
        
        connector.getOpenOrders().whenComplete((orders, throwable) -> {
            if (throwable == null && orders != null) {
                // Update active orders with latest status
                for (Order order : orders) {
                    Order activeOrder = activeOrders.get(order.getOrderId());
                    if (activeOrder != null && !activeOrder.getStatus().equals(order.getStatus())) {
                        activeOrder.setStatus(order.getStatus());
                        activeOrder.setFilledQuantity(order.getFilledQuantity());
                        activeOrder.setAverageFillPrice(order.getAverageFillPrice());
                        
                        // Trigger callback if available
                        Consumer<Order> callback = orderCallbacks.get(order.getOrderId());
                        if (callback != null) {
                            callback.accept(activeOrder);
                        }
                    }
                }
                
                // Remove completed orders
                activeOrders.entrySet().removeIf(entry -> {
                    Order order = entry.getValue();
                    return order.getStatus() == OrderStatus.FILLED || 
                           order.getStatus() == OrderStatus.CANCELLED ||
                           order.getStatus() == OrderStatus.REJECTED;
                });
            }
        });
    }
    
    // OrderUpdateListener implementation
    @Override
    public void onOrderUpdate(Order order) {
        logger.debug("Order update received: {}", order);
        
        Order activeOrder = activeOrders.get(order.getOrderId());
        if (activeOrder != null) {
            activeOrder.setStatus(order.getStatus());
            activeOrder.setFilledQuantity(order.getFilledQuantity());
            activeOrder.setAverageFillPrice(order.getAverageFillPrice());
            
            // Trigger callback
            Consumer<Order> callback = orderCallbacks.get(order.getOrderId());
            if (callback != null) {
                callback.accept(activeOrder);
            }
        }
    }
    
    @Override
    public void onOrderFilled(Order order) {
        logger.info("Order filled: {}", order);
        
        if (onOrderFilled != null) {
            onOrderFilled.accept(order);
        }
        
        // Remove from active orders and callbacks
        activeOrders.remove(order.getOrderId());
        orderCallbacks.remove(order.getOrderId());
    }
    
    @Override
    public void onOrderCancelled(Order order) {
        logger.info("Order cancelled: {}", order);
        
        if (onOrderCancelled != null) {
            onOrderCancelled.accept(order);
        }
        
        // Remove from active orders and callbacks
        activeOrders.remove(order.getOrderId());
        orderCallbacks.remove(order.getOrderId());
    }
    
    @Override
    public void onOrderError(String orderId, String error) {
        logger.error("Order error for {}: {}", orderId, error);
        
        if (onOrderError != null) {
            onOrderError.accept("Order " + orderId + ": " + error);
        }
        
        // Remove from active orders and callbacks
        activeOrders.remove(orderId);
        orderCallbacks.remove(orderId);
    }
    
    // Event listener setters
    public void setOnOrderFilled(Consumer<Order> onOrderFilled) {
        this.onOrderFilled = onOrderFilled;
    }
    
    public void setOnOrderCancelled(Consumer<Order> onOrderCancelled) {
        this.onOrderCancelled = onOrderCancelled;
    }
    
    public void setOnOrderError(Consumer<String> onOrderError) {
        this.onOrderError = onOrderError;
    }
    
    /**
     * Shutdown the service
     */
    public void shutdown() {
        logger.info("Shutting down Order Management Service");
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
