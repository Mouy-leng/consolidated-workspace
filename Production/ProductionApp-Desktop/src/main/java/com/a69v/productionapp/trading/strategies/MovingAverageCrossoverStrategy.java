package com.a69v.productionapp.trading.strategies;

import com.a69v.productionapp.trading.interfaces.TradingStrategy;
import com.a69v.productionapp.trading.model.Order;
import com.a69v.productionapp.trading.enums.OrderSide;
import com.a69v.productionapp.trading.enums.OrderType;
import com.a69v.productionapp.trading.services.ConfigurationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Simple Moving Average Crossover Strategy
 * Generates buy signals when fast MA crosses above slow MA
 * Generates sell signals when fast MA crosses below slow MA
 */
public class MovingAverageCrossoverStrategy implements TradingStrategy {
    private static final Logger logger = LoggerFactory.getLogger(MovingAverageCrossoverStrategy.class);
    
    private final ConfigurationService config;
    private final int fastPeriod;
    private final int slowPeriod;
    private final List<String> symbols;
    private final BigDecimal riskPerTrade;
    
    // Price history for each symbol
    private final Map<String, List<BigDecimal>> priceHistory = new ConcurrentHashMap<>();
    
    // Moving averages for each symbol
    private final Map<String, BigDecimal> fastMA = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> slowMA = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> previousFastMA = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> previousSlowMA = new ConcurrentHashMap<>();
    
    // Track positions to avoid multiple signals
    private final Map<String, OrderSide> currentSignal = new ConcurrentHashMap<>();
    
    private boolean enabled = false;
    
    public MovingAverageCrossoverStrategy(ConfigurationService config) {
        this.config = config;
        this.fastPeriod = config.getMovingAverageFastPeriod();
        this.slowPeriod = config.getMovingAverageSlowPeriod();
        this.symbols = config.getStrategySymbols("movingAverageCrossover");
        this.riskPerTrade = config.getStrategyRiskPerTrade("movingAverageCrossover")
            .orElse(config.getMaxRiskPerTrade());
        
        logger.info("Moving Average Crossover Strategy created - Fast: {}, Slow: {}, Symbols: {}", 
            fastPeriod, slowPeriod, symbols);
    }
    
    @Override
    public String getName() {
        return "MovingAverageCrossover";
    }
    
    @Override
    public List<String> getSymbols() {
        return new ArrayList<>(symbols);
    }
    
    @Override
    public void initialize() {
        enabled = config.isStrategyEnabled("movingAverageCrossover");
        
        // Initialize price history for each symbol
        for (String symbol : symbols) {
            priceHistory.put(symbol, new ArrayList<>());
            currentSignal.put(symbol, null);
        }
        
        logger.info("Moving Average Crossover Strategy initialized - Enabled: {}", enabled);
    }
    
    @Override
    public List<Order> onPriceUpdate(String symbol, BigDecimal bid, BigDecimal ask, long timestamp) {
        List<Order> orders = new ArrayList<>();
        
        if (!enabled || !symbols.contains(symbol)) {
            return orders;
        }
        
        // Use mid price for calculations
        BigDecimal midPrice = bid.add(ask).divide(BigDecimal.valueOf(2), 4, RoundingMode.HALF_UP);
        
        // Update price history
        List<BigDecimal> prices = priceHistory.get(symbol);
        prices.add(midPrice);
        
        // Keep only necessary history (slow period + some buffer)
        int maxHistory = slowPeriod + 10;
        if (prices.size() > maxHistory) {
            prices = prices.subList(prices.size() - maxHistory, prices.size());
            priceHistory.put(symbol, prices);
        }
        
        // Calculate moving averages if we have enough data
        if (prices.size() >= slowPeriod) {
            // Store previous MAs
            previousFastMA.put(symbol, fastMA.get(symbol));
            previousSlowMA.put(symbol, slowMA.get(symbol));
            
            // Calculate new MAs
            BigDecimal newFastMA = calculateMA(prices, fastPeriod);
            BigDecimal newSlowMA = calculateMA(prices, slowPeriod);
            
            fastMA.put(symbol, newFastMA);
            slowMA.put(symbol, newSlowMA);
            
            // Check for crossover signals
            OrderSide signal = detectCrossover(symbol);
            if (signal != null && !signal.equals(currentSignal.get(symbol))) {
                Order order = createOrder(symbol, signal, ask, bid);
                if (order != null) {
                    orders.add(order);
                    currentSignal.put(symbol, signal);
                    logger.info("Generated {} signal for {}: Fast MA = {}, Slow MA = {}", 
                        signal, symbol, newFastMA, newSlowMA);
                }
            }
        }
        
        return orders;
    }
    
    private BigDecimal calculateMA(List<BigDecimal> prices, int period) {
        if (prices.size() < period) {
            return BigDecimal.ZERO;
        }
        
        BigDecimal sum = BigDecimal.ZERO;
        for (int i = prices.size() - period; i < prices.size(); i++) {
            sum = sum.add(prices.get(i));
        }
        
        return sum.divide(BigDecimal.valueOf(period), 4, RoundingMode.HALF_UP);
    }
    
    private OrderSide detectCrossover(String symbol) {
        BigDecimal currentFast = fastMA.get(symbol);
        BigDecimal currentSlow = slowMA.get(symbol);
        BigDecimal prevFast = previousFastMA.get(symbol);
        BigDecimal prevSlow = previousSlowMA.get(symbol);
        
        if (currentFast == null || currentSlow == null || prevFast == null || prevSlow == null) {
            return null;
        }
        
        // Fast MA crosses above Slow MA - BUY signal
        if (prevFast.compareTo(prevSlow) <= 0 && currentFast.compareTo(currentSlow) > 0) {
            return OrderSide.BUY;
        }
        
        // Fast MA crosses below Slow MA - SELL signal
        if (prevFast.compareTo(prevSlow) >= 0 && currentFast.compareTo(currentSlow) < 0) {
            return OrderSide.SELL;
        }
        
        return null;
    }
    
    private Order createOrder(String symbol, OrderSide side, BigDecimal ask, BigDecimal bid) {
        try {
            Order order = new Order();
            order.setSymbol(symbol);
            order.setSide(side);
            order.setType(OrderType.MARKET);
            order.setClientOrderId("MA_CROSS_" + System.currentTimeMillis());
            
            // Set a base quantity - this will be adjusted by risk management
            order.setQuantity(new BigDecimal("10000")); // Base position size
            
            // Use market price
            BigDecimal price = side == OrderSide.BUY ? ask : bid;
            order.setPrice(price);
            
            // Calculate stop loss (2% of price)
            BigDecimal stopDistance = price.multiply(new BigDecimal("0.02"));
            BigDecimal stopPrice = side == OrderSide.BUY ? 
                price.subtract(stopDistance) : price.add(stopDistance);
            order.setStopPrice(stopPrice);
            
            return order;
        } catch (Exception e) {
            logger.error("Error creating order for {} {}: {}", side, symbol, e.getMessage());
            return null;
        }
    }
    
    @Override
    public boolean isEnabled() {
        return enabled;
    }
    
    @Override
    public void shutdown() {
        logger.info("Moving Average Crossover Strategy shutting down");
        priceHistory.clear();
        fastMA.clear();
        slowMA.clear();
        previousFastMA.clear();
        previousSlowMA.clear();
        currentSignal.clear();
    }
}