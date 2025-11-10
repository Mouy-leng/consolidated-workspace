package com.a69v.productionapp.trading.enums;

/**
 * Defines the status of an order throughout its lifecycle
 */
public enum OrderStatus {
    PENDING,
    SUBMITTED,
    ACCEPTED,
    PARTIALLY_FILLED,
    FILLED,
    CANCELLED,
    REJECTED,
    EXPIRED
}