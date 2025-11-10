package com.a69v.productionapp.trading;

import com.a69v.productionapp.trading.connectors.MetaTraderConnector;
import com.a69v.productionapp.trading.connectors.OandaConnector;
import com.a69v.productionapp.trading.interfaces.MarketDataListener;
import com.a69v.productionapp.trading.interfaces.TradingConnector;
import com.a69v.productionapp.trading.model.Account;
import com.a69v.productionapp.trading.model.Order;
import com.a69v.productionapp.trading.model.Position;
import com.a69v.productionapp.trading.enums.OrderSide;
import com.a69v.productionapp.trading.enums.OrderType;
import com.a69v.productionapp.trading.services.ConfigurationService;
import com.a69v.productionapp.trading.services.OrderManagementService;
import com.a69v.productionapp.trading.services.RiskManagementService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

/**
 * Main Trading System Manager that orchestrates all trading components
 */
public class TradingSystemManager implements MarketDataListener {
    private static final Logger logger = LoggerFactory.getLogger(TradingSystemManager.class);
    
    private final ConfigurationService configService;
    private final RiskManagementService riskService;
    private final ScheduledExecutorService scheduler;
    private final ExecutorService executor;
    
    private TradingConnector primaryConnector;
    private OrderManagementService orderService;
    private Account currentAccount;
    private List<Position> currentPositions;
    
    private volatile boolean running = false;
    private volatile boolean connected = false;
    
    // System monitoring
    private long lastHeartbeat = System.currentTimeMillis();
    private int connectionAttempts = 0;
    
    public TradingSystemManager() {
        this.configService = new ConfigurationService();
        this.riskService = new RiskManagementService();
        this.scheduler = Executors.newScheduledThreadPool(4);
        this.executor = Executors.newFixedThreadPool(8);
        this.currentPositions = new ArrayList<>();
        
        logger.info("Trading System Manager initialized");
        configService.logConfiguration();
        
        // Apply configuration to risk service
        applyRiskConfiguration();
    }
    
    /**
     * Start the trading system
     */
    public void start() throws Exception {
        logger.info("Starting Trading System...");
        running = true;
        
        // Initialize connectors
        initializeConnectors();
        
        // Connect to broker
        connectToBroker();
        
        // Initialize order management
        initializeOrderManagement();
        
        // Start monitoring tasks
        startMonitoringTasks();
        
        // Subscribe to market data
        subscribeToMarketData();
        
        logger.info("Trading System started successfully");
    }
    
    /**
     * Shutdown the trading system
     */
    public void shutdown() {
        logger.info("Shutting down Trading System...");
        running = false;
        
        try {
            // Emergency stop if needed
            if (orderService != null) {
                orderService.emergencyStop().get(30, TimeUnit.SECONDS);
                orderService.shutdown();
            }
            
            // Disconnect from broker
            if (primaryConnector != null && primaryConnector.isConnected()) {
                primaryConnector.disconnect().get(30, TimeUnit.SECONDS);
            }
            
            // Shutdown executors
            scheduler.shutdown();
            executor.shutdown();
            
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
            
            logger.info("Trading System shutdown complete");
        } catch (Exception e) {
            logger.error("Error during shutdown: {}", e.getMessage());
        }
    }
    
    /**
     * Place a manual trade order
     */
    public CompletableFuture<Order> placeOrder(String symbol, OrderSide side, OrderType type, 
                                             BigDecimal quantity, BigDecimal price) {
        if (!connected || !running) {
            return CompletableFuture.failedFuture(new IllegalStateException("Trading system not connected"));
        }
        
        Order order = new Order();
        order.setSymbol(symbol);
        order.setSide(side);
        order.setType(type);
        order.setQuantity(quantity);
        order.setPrice(price);
        order.setClientOrderId("MANUAL_" + System.currentTimeMillis());
        
        return placeOrderWithRiskCheck(order);
    }
    
    /**
     * Place order with risk management validation
     */
    private CompletableFuture<Order> placeOrderWithRiskCheck(Order order) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Validate with risk management
                RiskManagementService.RiskValidationResult validation = 
                    riskService.validateOrder(order, currentAccount, currentPositions);
                    
                if (!validation.isValid()) {
                    throw new RuntimeException("Risk validation failed: " + validation.getMessage());
                }
                
                logger.info("Order validated - Risk: {}, Position Size: {}", 
                    validation.getRiskAmount(), validation.getPositionSize());
                
                return order;
            } catch (Exception e) {
                logger.error("Risk validation failed: {}", e.getMessage());
                throw new RuntimeException(e);
            }
        }, executor).thenCompose(validatedOrder -> {
            return orderService.placeOrder(validatedOrder, (filledOrder) -> {
                // Order callback - update risk tracking
                riskService.onOrderFilled(filledOrder, currentAccount);
                logger.info("Order filled: {}", filledOrder);
            });
        });
    }
    
    /**
     * Cancel an order
     */
    public CompletableFuture<Boolean> cancelOrder(String orderId) {
        if (orderService == null) {
            return CompletableFuture.failedFuture(new IllegalStateException("Order service not initialized"));
        }
        return orderService.cancelOrder(orderId);
    }
    
    /**
     * Close a position
     */
    public CompletableFuture<Boolean> closePosition(String symbol) {
        if (orderService == null) {
            return CompletableFuture.failedFuture(new IllegalStateException("Order service not initialized"));
        }
        return orderService.closeAllPositions(symbol);
    }
    
    /**
     * Get current account information
     */
    public Account getCurrentAccount() {
        return currentAccount;
    }
    
    /**
     * Get current positions
     */
    public List<Position> getCurrentPositions() {
        return new ArrayList<>(currentPositions);
    }
    
    /**
     * Get risk management statistics
     */
    public RiskManagementService getRiskService() {
        return riskService;
    }
    
    /**
     * Check if system is running and connected
     */
    public boolean isRunning() {
        return running && connected;
    }
    
    // Private initialization methods
    
    private void initializeConnectors() throws Exception {
        logger.info("Initializing trading connectors...");
        
        if (configService.isMetaTraderEnabled()) {
            primaryConnector = new MetaTraderConnector(
                configService.getMetaTraderHost(),
                configService.getMetaTraderPort(),
                configService.getMetaTraderApiKey()
            );
            logger.info("MetaTrader connector initialized");
        } else if (configService.isOandaEnabled()) {
            primaryConnector = new OandaConnector(
                configService.getOandaAccountId(),
                configService.getOandaApiKey(),
                configService.isOandaLive()
            );
            logger.info("OANDA connector initialized");
        } else {
            throw new IllegalStateException("No trading connector enabled in configuration");
        }
    }
    
    private void connectToBroker() throws Exception {
        logger.info("Connecting to broker...");
        
        int maxAttempts = configService.getMaxReconnectAttempts();
        int delay = configService.getReconnectDelay();
        
        for (connectionAttempts = 1; connectionAttempts <= maxAttempts; connectionAttempts++) {
            try {
                boolean success = primaryConnector.connect().get(30, TimeUnit.SECONDS);
                if (success) {
                    connected = true;
                    logger.info("Connected to broker: {}", primaryConnector.getConnectorName());
                    return;
                }
            } catch (Exception e) {
                logger.warn("Connection attempt {} failed: {}", connectionAttempts, e.getMessage());
                if (connectionAttempts < maxAttempts) {
                    Thread.sleep(delay * 1000);
                }
            }
        }
        
        throw new RuntimeException("Failed to connect to broker after " + maxAttempts + " attempts");
    }
    
    private void initializeOrderManagement() {
        logger.info("Initializing order management...");
        orderService = new OrderManagementService(primaryConnector);
        
        // Set up event handlers
        orderService.setOnOrderFilled(order -> {
            logger.info("Order filled notification: {}", order);
            riskService.onOrderFilled(order, currentAccount);
        });
        
        orderService.setOnOrderCancelled(order -> {
            logger.info("Order cancelled notification: {}", order);
        });
        
        orderService.setOnOrderError(error -> {
            logger.error("Order error: {}", error);
        });
    }
    
    private void startMonitoringTasks() {
        logger.info("Starting monitoring tasks...");
        
        // Account monitoring
        scheduler.scheduleAtFixedRate(this::updateAccountInfo, 
            0, configService.getAccountUpdateInterval(), TimeUnit.SECONDS);
            
        // Position monitoring
        scheduler.scheduleAtFixedRate(this::updatePositions, 
            5, 10, TimeUnit.SECONDS);
            
        // Risk monitoring
        scheduler.scheduleAtFixedRate(this::monitorRisk, 
            10, 30, TimeUnit.SECONDS);
            
        // System health monitoring
        scheduler.scheduleAtFixedRate(this::monitorSystemHealth, 
            30, 60, TimeUnit.SECONDS);
    }
    
    private void subscribeToMarketData() {
        logger.info("Subscribing to market data...");
        List<String> symbols = configService.getMarketDataSymbols();
        primaryConnector.subscribeToMarketData(symbols, this);
    }
    
    private void applyRiskConfiguration() {
        riskService.setMaxRiskPerTrade(configService.getMaxRiskPerTrade());
        riskService.setMaxPortfolioRisk(configService.getMaxPortfolioRisk());
        riskService.setMaxDrawdown(configService.getMaxDrawdown());
        riskService.setMaxPositionSize(configService.getMaxPositionSize());
        riskService.setMaxOpenPositions(configService.getMaxOpenPositions());
        
        logger.info("Risk management configuration applied");
    }
    
    // Monitoring tasks
    
    private void updateAccountInfo() {
        if (!connected || !running) return;
        
        try {
            primaryConnector.getAccount().whenComplete((account, throwable) -> {
                if (throwable == null && account != null) {
                    currentAccount = account;
                    lastHeartbeat = System.currentTimeMillis();
                } else {
                    logger.warn("Failed to update account info: {}", 
                        throwable != null ? throwable.getMessage() : "Unknown error");
                }
            });
        } catch (Exception e) {
            logger.error("Error updating account info: {}", e.getMessage());
        }
    }
    
    private void updatePositions() {
        if (!connected || !running) return;
        
        try {
            primaryConnector.getPositions().whenComplete((positions, throwable) -> {
                if (throwable == null && positions != null) {
                    currentPositions = positions;
                } else {
                    logger.warn("Failed to update positions: {}", 
                        throwable != null ? throwable.getMessage() : "Unknown error");
                }
            });
        } catch (Exception e) {
            logger.error("Error updating positions: {}", e.getMessage());
        }
    }
    
    private void monitorRisk() {
        if (currentAccount == null || !running) return;
        
        try {
            // Check for emergency stop conditions
            if (configService.isEmergencyStopEnabled() && riskService.shouldTriggerEmergencyStop(currentAccount)) {
                logger.error("EMERGENCY STOP TRIGGERED - Stopping all trading");
                orderService.emergencyStop();
            }
            
            // Log risk metrics
            BigDecimal drawdown = riskService.calculateDrawdown(currentAccount);
            logger.info("Risk Metrics - Portfolio Risk: {}, Drawdown: {}, Emergency Stop: {}", 
                riskService.getTotalPortfolioRisk(), drawdown, riskService.isEmergencyStopTriggered());
                
        } catch (Exception e) {
            logger.error("Error monitoring risk: {}", e.getMessage());
        }
    }
    
    private void monitorSystemHealth() {
        long currentTime = System.currentTimeMillis();
        long timeSinceHeartbeat = currentTime - lastHeartbeat;
        
        if (timeSinceHeartbeat > 60000) { // 1 minute
            logger.warn("No heartbeat from broker in {} ms", timeSinceHeartbeat);
            
            // Attempt to reconnect if needed
            if (!primaryConnector.isConnected()) {
                logger.info("Attempting to reconnect to broker...");
                try {
                    connectToBroker();
                } catch (Exception e) {
                    logger.error("Reconnection failed: {}", e.getMessage());
                }
            }
        }
        
        logger.info("System Health - Running: {}, Connected: {}, Positions: {}, Orders: {}", 
            running, connected, currentPositions.size(), 
            orderService != null ? orderService.getActiveOrders().size() : 0);
    }
    
    // MarketDataListener implementation
    
    @Override
    public void onPriceUpdate(String symbol, BigDecimal bid, BigDecimal ask, long timestamp) {
        logger.debug("Price update - {}: bid={}, ask={}", symbol, bid, ask);
        lastHeartbeat = System.currentTimeMillis();
    }
    
    @Override
    public void onMarketDataError(String error) {
        logger.error("Market data error: {}", error);
    }
}