package com.a69v.productionapp.trading.services;

import com.a69v.productionapp.trading.model.Account;
import com.a69v.productionapp.trading.model.Order;
import com.a69v.productionapp.trading.model.Position;
import com.a69v.productionapp.trading.enums.OrderSide;
import com.a69v.productionapp.trading.enums.OrderType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Risk Management Service that implements trading risk controls
 */
public class RiskManagementService {
    private static final Logger logger = LoggerFactory.getLogger(RiskManagementService.class);
    
    // Risk parameters
    private BigDecimal maxRiskPerTrade = new BigDecimal("0.02"); // 2% per trade
    private BigDecimal maxPortfolioRisk = new BigDecimal("0.10"); // 10% total portfolio risk
    private BigDecimal maxDrawdown = new BigDecimal("0.15"); // 15% max drawdown
    private BigDecimal maxPositionSize = new BigDecimal("0.25"); // 25% max position size
    private int maxOpenPositions = 10;
    private BigDecimal minAccountBalance = new BigDecimal("1000"); // Minimum balance to trade
    
    // Position sizing parameters
    private BigDecimal defaultRiskRewardRatio = new BigDecimal("2.0"); // 1:2 risk/reward
    private BigDecimal volatilityMultiplier = new BigDecimal("1.5");
    
    // Tracking
    private final Map<String, BigDecimal> symbolRisk = new ConcurrentHashMap<>();
    private BigDecimal totalPortfolioRisk = BigDecimal.ZERO;
    private BigDecimal highWaterMark = BigDecimal.ZERO;
    private boolean emergencyStopTriggered = false;
    
    public RiskManagementService() {
        logger.info("Risk Management Service initialized with default parameters");
    }
    
    /**
     * Validate if an order meets risk management criteria
     */
    public RiskValidationResult validateOrder(Order order, Account account, List<Position> positions) {
        logger.debug("Validating order: {}", order);
        
        // Check if emergency stop is active
        if (emergencyStopTriggered) {
            return new RiskValidationResult(false, "Emergency stop is active - no new orders allowed");
        }
        
        // Check minimum balance
        if (account.getBalance().compareTo(minAccountBalance) < 0) {
            return new RiskValidationResult(false, "Account balance below minimum required: " + minAccountBalance);
        }
        
        // Check maximum open positions
        if (positions.size() >= maxOpenPositions) {
            return new RiskValidationResult(false, "Maximum open positions reached: " + maxOpenPositions);
        }
        
        // Calculate position size and risk
        BigDecimal positionSize = calculatePositionSize(order, account);
        if (positionSize.compareTo(BigDecimal.ZERO) <= 0) {
            return new RiskValidationResult(false, "Invalid position size calculated");
        }
        
        // Check maximum position size
        BigDecimal positionValue = positionSize.multiply(order.getPrice() != null ? order.getPrice() : BigDecimal.ONE);
        BigDecimal positionRatio = positionValue.divide(account.getEquity(), 4, RoundingMode.HALF_UP);
        
        if (positionRatio.compareTo(maxPositionSize) > 0) {
            return new RiskValidationResult(false, "Position size exceeds maximum allowed: " + 
                positionRatio + " > " + maxPositionSize);
        }
        
        // Calculate trade risk
        BigDecimal tradeRisk = calculateTradeRisk(order, account);
        BigDecimal riskRatio = tradeRisk.divide(account.getEquity(), 4, RoundingMode.HALF_UP);
        
        if (riskRatio.compareTo(maxRiskPerTrade) > 0) {
            return new RiskValidationResult(false, "Trade risk exceeds maximum per trade: " + 
                riskRatio + " > " + maxRiskPerTrade);
        }
        
        // Check total portfolio risk
        BigDecimal newTotalRisk = totalPortfolioRisk.add(tradeRisk);
        BigDecimal newRiskRatio = newTotalRisk.divide(account.getEquity(), 4, RoundingMode.HALF_UP);
        
        if (newRiskRatio.compareTo(maxPortfolioRisk) > 0) {
            return new RiskValidationResult(false, "Total portfolio risk would exceed maximum: " + 
                newRiskRatio + " > " + maxPortfolioRisk);
        }
        
        // Check drawdown
        BigDecimal currentDrawdown = calculateDrawdown(account);
        if (currentDrawdown.compareTo(maxDrawdown) > 0) {
            return new RiskValidationResult(false, "Maximum drawdown exceeded: " + 
                currentDrawdown + " > " + maxDrawdown);
        }
        
        // Update the order with calculated position size
        order.setQuantity(positionSize);
        
        return new RiskValidationResult(true, "Order validated successfully", positionSize, tradeRisk);
    }
    
    /**
     * Calculate position size based on risk management rules
     */
    public BigDecimal calculatePositionSize(Order order, Account account) {
        if (order.getPrice() == null || order.getStopPrice() == null) {
            // Use default position sizing if no stop price is set
            return account.getEquity()
                .multiply(maxRiskPerTrade)
                .divide(order.getPrice() != null ? order.getPrice() : BigDecimal.ONE, 4, RoundingMode.HALF_UP);
        }
        
        // Calculate position size based on stop loss
        BigDecimal entryPrice = order.getPrice();
        BigDecimal stopPrice = order.getStopPrice();
        BigDecimal riskPerUnit = entryPrice.subtract(stopPrice).abs();
        
        if (riskPerUnit.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        
        BigDecimal riskAmount = account.getEquity().multiply(maxRiskPerTrade);
        BigDecimal positionSize = riskAmount.divide(riskPerUnit, 4, RoundingMode.HALF_UP);
        
        // Apply maximum position size constraint
        BigDecimal maxSize = account.getEquity()
            .multiply(maxPositionSize)
            .divide(entryPrice, 4, RoundingMode.HALF_UP);
            
        return positionSize.min(maxSize);
    }
    
    /**
     * Calculate trade risk amount
     */
    public BigDecimal calculateTradeRisk(Order order, Account account) {
        if (order.getPrice() == null || order.getStopPrice() == null) {
            // Default risk calculation
            return order.getQuantity()
                .multiply(order.getPrice() != null ? order.getPrice() : BigDecimal.ONE)
                .multiply(maxRiskPerTrade);
        }
        
        BigDecimal entryPrice = order.getPrice();
        BigDecimal stopPrice = order.getStopPrice();
        BigDecimal riskPerUnit = entryPrice.subtract(stopPrice).abs();
        
        return order.getQuantity().multiply(riskPerUnit);
    }
    
    /**
     * Calculate current drawdown
     */
    public BigDecimal calculateDrawdown(Account account) {
        if (highWaterMark.compareTo(account.getEquity()) < 0) {
            highWaterMark = account.getEquity();
            return BigDecimal.ZERO;
        }
        
        if (highWaterMark.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        
        BigDecimal drawdown = highWaterMark.subtract(account.getEquity())
            .divide(highWaterMark, 4, RoundingMode.HALF_UP);
            
        return drawdown.max(BigDecimal.ZERO);
    }
    
    /**
     * Add stop loss and take profit to an order
     */
    public Order addRiskControls(Order order, BigDecimal stopLossDistance, BigDecimal takeProfitDistance) {
        if (order.getPrice() == null) {
            logger.warn("Cannot add risk controls to market order without price");
            return order;
        }
        
        BigDecimal entryPrice = order.getPrice();
        
        // Calculate stop loss
        BigDecimal stopPrice;
        if (order.getSide() == OrderSide.BUY) {
            stopPrice = entryPrice.subtract(stopLossDistance);
        } else {
            stopPrice = entryPrice.add(stopLossDistance);
        }
        order.setStopPrice(stopPrice);
        
        logger.info("Added stop loss at {} for order {}", stopPrice, order.getOrderId());
        return order;
    }
    
    /**
     * Update risk tracking when order is filled
     */
    public void onOrderFilled(Order order, Account account) {
        BigDecimal tradeRisk = calculateTradeRisk(order, account);
        
        // Add to symbol risk tracking
        symbolRisk.merge(order.getSymbol(), tradeRisk, BigDecimal::add);
        
        // Update total portfolio risk
        totalPortfolioRisk = totalPortfolioRisk.add(tradeRisk);
        
        logger.info("Updated risk tracking - Symbol: {} Risk: {}, Total Portfolio Risk: {}", 
            order.getSymbol(), tradeRisk, totalPortfolioRisk);
    }
    
    /**
     * Update risk tracking when position is closed
     */
    public void onPositionClosed(String symbol, BigDecimal realizedPnL) {
        // Remove symbol risk
        BigDecimal symbolRiskAmount = symbolRisk.getOrDefault(symbol, BigDecimal.ZERO);
        totalPortfolioRisk = totalPortfolioRisk.subtract(symbolRiskAmount);
        symbolRisk.remove(symbol);
        
        logger.info("Position closed - Symbol: {}, Realized PnL: {}, Remaining Portfolio Risk: {}", 
            symbol, realizedPnL, totalPortfolioRisk);
    }
    
    /**
     * Check if emergency stop should be triggered
     */
    public boolean shouldTriggerEmergencyStop(Account account) {
        BigDecimal currentDrawdown = calculateDrawdown(account);
        
        if (currentDrawdown.compareTo(maxDrawdown) > 0 && !emergencyStopTriggered) {
            emergencyStopTriggered = true;
            logger.error("EMERGENCY STOP TRIGGERED - Drawdown: {} exceeds maximum: {}", 
                currentDrawdown, maxDrawdown);
            return true;
        }
        
        return false;
    }
    
    /**
     * Reset emergency stop (manual intervention required)
     */
    public void resetEmergencyStop() {
        emergencyStopTriggered = false;
        logger.warn("Emergency stop manually reset");
    }
    
    // Getters and Setters for risk parameters
    public BigDecimal getMaxRiskPerTrade() { return maxRiskPerTrade; }
    public void setMaxRiskPerTrade(BigDecimal maxRiskPerTrade) { 
        this.maxRiskPerTrade = maxRiskPerTrade; 
        logger.info("Max risk per trade updated to: {}", maxRiskPerTrade);
    }
    
    public BigDecimal getMaxPortfolioRisk() { return maxPortfolioRisk; }
    public void setMaxPortfolioRisk(BigDecimal maxPortfolioRisk) { 
        this.maxPortfolioRisk = maxPortfolioRisk; 
        logger.info("Max portfolio risk updated to: {}", maxPortfolioRisk);
    }
    
    public BigDecimal getMaxDrawdown() { return maxDrawdown; }
    public void setMaxDrawdown(BigDecimal maxDrawdown) { 
        this.maxDrawdown = maxDrawdown; 
        logger.info("Max drawdown updated to: {}", maxDrawdown);
    }
    
    public BigDecimal getMaxPositionSize() { return maxPositionSize; }
    public void setMaxPositionSize(BigDecimal maxPositionSize) { 
        this.maxPositionSize = maxPositionSize; 
        logger.info("Max position size updated to: {}", maxPositionSize);
    }
    
    public int getMaxOpenPositions() { return maxOpenPositions; }
    public void setMaxOpenPositions(int maxOpenPositions) { 
        this.maxOpenPositions = maxOpenPositions; 
        logger.info("Max open positions updated to: {}", maxOpenPositions);
    }
    
    public boolean isEmergencyStopTriggered() { return emergencyStopTriggered; }
    public BigDecimal getTotalPortfolioRisk() { return totalPortfolioRisk; }
    public Map<String, BigDecimal> getSymbolRisk() { return new ConcurrentHashMap<>(symbolRisk); }
    
    /**
     * Risk validation result class
     */
    public static class RiskValidationResult {
        private final boolean valid;
        private final String message;
        private final BigDecimal positionSize;
        private final BigDecimal riskAmount;
        
        public RiskValidationResult(boolean valid, String message) {
            this(valid, message, null, null);
        }
        
        public RiskValidationResult(boolean valid, String message, BigDecimal positionSize, BigDecimal riskAmount) {
            this.valid = valid;
            this.message = message;
            this.positionSize = positionSize;
            this.riskAmount = riskAmount;
        }
        
        public boolean isValid() { return valid; }
        public String getMessage() { return message; }
        public BigDecimal getPositionSize() { return positionSize; }
        public BigDecimal getRiskAmount() { return riskAmount; }
    }
}