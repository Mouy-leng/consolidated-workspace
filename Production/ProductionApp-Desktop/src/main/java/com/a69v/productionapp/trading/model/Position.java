package com.a69v.productionapp.trading.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Represents a trading position
 */
public class Position {
    private String symbol;
    private BigDecimal quantity;
    private BigDecimal averagePrice;
    private BigDecimal unrealizedPnL;
    private BigDecimal realizedPnL;
    private LocalDateTime openedAt;
    private LocalDateTime updatedAt;
    
    public Position() {
        this.openedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.unrealizedPnL = BigDecimal.ZERO;
        this.realizedPnL = BigDecimal.ZERO;
    }
    
    public Position(String symbol, BigDecimal quantity, BigDecimal averagePrice) {
        this();
        this.symbol = symbol;
        this.quantity = quantity;
        this.averagePrice = averagePrice;
    }
    
    // Getters and Setters
    public String getSymbol() { return symbol; }
    public void setSymbol(String symbol) { this.symbol = symbol; }
    
    public BigDecimal getQuantity() { return quantity; }
    public void setQuantity(BigDecimal quantity) { this.quantity = quantity; }
    
    public BigDecimal getAveragePrice() { return averagePrice; }
    public void setAveragePrice(BigDecimal averagePrice) { this.averagePrice = averagePrice; }
    
    public BigDecimal getUnrealizedPnL() { return unrealizedPnL; }
    public void setUnrealizedPnL(BigDecimal unrealizedPnL) { 
        this.unrealizedPnL = unrealizedPnL;
        this.updatedAt = LocalDateTime.now();
    }
    
    public BigDecimal getRealizedPnL() { return realizedPnL; }
    public void setRealizedPnL(BigDecimal realizedPnL) { this.realizedPnL = realizedPnL; }
    
    public LocalDateTime getOpenedAt() { return openedAt; }
    public void setOpenedAt(LocalDateTime openedAt) { this.openedAt = openedAt; }
    
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    
    public boolean isLong() { return quantity.compareTo(BigDecimal.ZERO) > 0; }
    public boolean isShort() { return quantity.compareTo(BigDecimal.ZERO) < 0; }
    public boolean isClosed() { return quantity.equals(BigDecimal.ZERO); }
    
    @Override
    public String toString() {
        return String.format("Position{symbol='%s', qty=%s, avgPrice=%s, unrealizedPnL=%s}",
                symbol, quantity, averagePrice, unrealizedPnL);
    }
}