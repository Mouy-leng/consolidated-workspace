package com.a69v.productionapp.trading.services;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Configuration service for managing trading system settings
 */
public class ConfigurationService {
    private static final Logger logger = LoggerFactory.getLogger(ConfigurationService.class);
    
    private final Config config;
    
    public ConfigurationService() {
        this.config = ConfigFactory.load();
        logger.info("Configuration loaded successfully");
    }
    
    public ConfigurationService(String configFile) {
        this.config = ConfigFactory.load(configFile);
        logger.info("Configuration loaded from: {}", configFile);
    }
    
    // Broker Configuration
    public boolean isMetaTraderEnabled() {
        return config.getBoolean("trading.brokers.metatrader.enabled");
    }
    
    public String getMetaTraderHost() {
        return config.getString("trading.brokers.metatrader.host");
    }
    
    public int getMetaTraderPort() {
        return config.getInt("trading.brokers.metatrader.port");
    }
    
    public String getMetaTraderApiKey() {
        return config.getString("trading.brokers.metatrader.apiKey");
    }
    
    public boolean isOandaEnabled() {
        return config.getBoolean("trading.brokers.oanda.enabled");
    }
    
    public String getOandaAccountId() {
        return config.getString("trading.brokers.oanda.accountId");
    }
    
    public String getOandaApiKey() {
        return config.getString("trading.brokers.oanda.apiKey");
    }
    
    public boolean isOandaLive() {
        return config.getBoolean("trading.brokers.oanda.isLive");
    }
    
    // Risk Management Configuration
    public BigDecimal getMaxRiskPerTrade() {
        return new BigDecimal(config.getString("trading.risk.maxRiskPerTrade"));
    }
    
    public BigDecimal getMaxPortfolioRisk() {
        return new BigDecimal(config.getString("trading.risk.maxPortfolioRisk"));
    }
    
    public BigDecimal getMaxDrawdown() {
        return new BigDecimal(config.getString("trading.risk.maxDrawdown"));
    }
    
    public BigDecimal getMaxPositionSize() {
        return new BigDecimal(config.getString("trading.risk.maxPositionSize"));
    }
    
    public int getMaxOpenPositions() {
        return config.getInt("trading.risk.maxOpenPositions");
    }
    
    public BigDecimal getMinAccountBalance() {
        return new BigDecimal(config.getString("trading.risk.minAccountBalance"));
    }
    
    public BigDecimal getDefaultRiskRewardRatio() {
        return new BigDecimal(config.getString("trading.risk.defaultRiskRewardRatio"));
    }
    
    public BigDecimal getVolatilityMultiplier() {
        return new BigDecimal(config.getString("trading.risk.volatilityMultiplier"));
    }
    
    // Strategy Configuration
    public boolean isStrategyEnabled(String strategyName) {
        try {
            return config.getBoolean(String.format("trading.strategies.%s.enabled", strategyName));
        } catch (Exception e) {
            logger.warn("Strategy {} not found in configuration", strategyName);
            return false;
        }
    }
    
    public List<String> getStrategySymbols(String strategyName) {
        return config.getStringList(String.format("trading.strategies.%s.symbols", strategyName));
    }
    
    public String getStrategyTimeframe(String strategyName) {
        return config.getString(String.format("trading.strategies.%s.timeframe", strategyName));
    }
    
    public Optional<BigDecimal> getStrategyRiskPerTrade(String strategyName) {
        try {
            String value = config.getString(String.format("trading.strategies.%s.riskPerTrade", strategyName));
            return Optional.of(new BigDecimal(value));
        } catch (Exception e) {
            return Optional.empty();
        }
    }
    
    // Moving Average Crossover Strategy specific
    public int getMovingAverageFastPeriod() {
        return config.getInt("trading.strategies.movingAverageCrossover.fastPeriod");
    }
    
    public int getMovingAverageSlowPeriod() {
        return config.getInt("trading.strategies.movingAverageCrossover.slowPeriod");
    }
    
    // Mean Reversion Strategy specific
    public int getMeanReversionLookbackPeriod() {
        return config.getInt("trading.strategies.meanReversion.lookbackPeriod");
    }
    
    public BigDecimal getMeanReversionDeviationThreshold() {
        return new BigDecimal(config.getString("trading.strategies.meanReversion.deviationThreshold"));
    }
    
    // Market Data Configuration
    public int getMarketDataUpdateInterval() {
        return config.getInt("trading.marketData.updateInterval");
    }
    
    public List<String> getMarketDataSymbols() {
        return config.getStringList("trading.marketData.symbols");
    }
    
    public int getMaxHistoryDays() {
        return config.getInt("trading.marketData.maxHistoryDays");
    }
    
    // Logging Configuration
    public String getLoggingLevel() {
        return config.getString("trading.logging.level");
    }
    
    public boolean isFileLoggingEnabled() {
        return config.getBoolean("trading.logging.enableFileLogging");
    }
    
    public String getLogDirectory() {
        return config.getString("trading.logging.logDirectory");
    }
    
    public String getMaxFileSize() {
        return config.getString("trading.logging.maxFileSize");
    }
    
    public int getMaxFiles() {
        return config.getInt("trading.logging.maxFiles");
    }
    
    // System Configuration
    public int getOrderUpdateInterval() {
        return config.getInt("trading.system.orderUpdateInterval");
    }
    
    public int getAccountUpdateInterval() {
        return config.getInt("trading.system.accountUpdateInterval");
    }
    
    public boolean isEmergencyStopEnabled() {
        return config.getBoolean("trading.system.emergencyStopEnabled");
    }
    
    public int getMaxReconnectAttempts() {
        return config.getInt("trading.system.maxReconnectAttempts");
    }
    
    public int getReconnectDelay() {
        return config.getInt("trading.system.reconnectDelay");
    }
    
    // Utility methods
    public Config getRawConfig() {
        return config;
    }
    
    public boolean hasPath(String path) {
        return config.hasPath(path);
    }
    
    public void logConfiguration() {
        logger.info("Trading System Configuration:");
        logger.info("  MetaTrader enabled: {}", isMetaTraderEnabled());
        logger.info("  OANDA enabled: {}", isOandaEnabled());
        logger.info("  Max risk per trade: {}", getMaxRiskPerTrade());
        logger.info("  Max portfolio risk: {}", getMaxPortfolioRisk());
        logger.info("  Max drawdown: {}", getMaxDrawdown());
        logger.info("  Max open positions: {}", getMaxOpenPositions());
        logger.info("  Market data symbols: {}", getMarketDataSymbols());
        logger.info("  Emergency stop enabled: {}", isEmergencyStopEnabled());
    }
}
