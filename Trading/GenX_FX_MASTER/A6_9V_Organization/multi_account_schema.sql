-- Multi-Account Database Schema for GenX_FX
CREATE TABLE IF NOT EXISTS accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    broker VARCHAR(100) NOT NULL,
    account_type ENUM('demo', 'live') DEFAULT 'demo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trading_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    total_trades INT DEFAULT 0,
    profit_loss DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS signals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    symbol VARCHAR(20) NOT NULL,
    action ENUM('BUY', 'SELL', 'HOLD') NOT NULL,
    entry_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),
    confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Insert sample accounts
INSERT IGNORE INTO accounts (email, broker, account_type) VALUES 
('Example1@gmail.com', 'FXCM', 'demo'),
('Example2@gmail.com', 'Exness', 'demo');