package com.a69v.productionapp.trading.model;

import java.math.BigDecimal;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

/**
 * Represents a trading account
 */
public class Account {
    private String accountId;
    private BigDecimal balance;
    private BigDecimal equity;
    private BigDecimal margin;
    private BigDecimal freeMargin;
    private BigDecimal marginLevel;
    private String currency;
    private Map<String, Position> positions;
    
    public Account() {
        this.positions = new ConcurrentHashMap<>();
        this.balance = BigDecimal.ZERO;
        this.equity = BigDecimal.ZERO;
        this.margin = BigDecimal.ZERO;
        this.freeMargin = BigDecimal.ZERO;
        this.marginLevel = BigDecimal.ZERO;
    }
    
    public Account(String accountId, String currency) {
        this();
        this.accountId = accountId;
        this.currency = currency;
    }
    
    // Getters and Setters
    public String getAccountId() { return accountId; }
    public void setAccountId(String accountId) { this.accountId = accountId; }
    
    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal balance) { this.balance = balance; }
    
    public BigDecimal getEquity() { return equity; }
    public void setEquity(BigDecimal equity) { this.equity = equity; }
    
    public BigDecimal getMargin() { return margin; }
    public void setMargin(BigDecimal margin) { this.margin = margin; }
    
    public BigDecimal getFreeMargin() { return freeMargin; }
    public void setFreeMargin(BigDecimal freeMargin) { this.freeMargin = freeMargin; }
    
    public BigDecimal getMarginLevel() { return marginLevel; }
    public void setMarginLevel(BigDecimal marginLevel) { this.marginLevel = marginLevel; }
    
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    
    public Map<String, Position> getPositions() { return positions; }
    public void setPositions(Map<String, Position> positions) { this.positions = positions; }
    
    public void addPosition(Position position) {
        positions.put(position.getSymbol(), position);
    }
    
    public void removePosition(String symbol) {
        positions.remove(symbol);
    }
    
    public Position getPosition(String symbol) {
        return positions.get(symbol);
    }
    
    public boolean hasPosition(String symbol) {
        return positions.containsKey(symbol) && !positions.get(symbol).isClosed();
    }
    
    @Override
    public String toString() {
        return String.format("Account{id='%s', balance=%s, equity=%s, currency='%s', positions=%d}",
                accountId, balance, equity, currency, positions.size());
    }
}