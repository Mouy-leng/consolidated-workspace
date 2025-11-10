-- Multi-tenant account support

-- Agents table (logical agent per user)
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link multiple broker accounts per agent
CREATE TABLE IF NOT EXISTS agent_accounts (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    broker VARCHAR(50) NOT NULL,
    account_alias VARCHAR(100) NOT NULL,
    account_number VARCHAR(100),
    environment VARCHAR(20) DEFAULT 'demo', -- demo/live
    api_key TEXT,
    api_secret TEXT,
    extra JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scope trades to specific agent_account
ALTER TABLE IF EXISTS trades
    ADD COLUMN IF NOT EXISTS agent_account_id INTEGER REFERENCES agent_accounts(id);

-- Persist per-agent context/state
CREATE TABLE IF NOT EXISTS agent_context (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    context_key VARCHAR(100) NOT NULL,
    context_value JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_context ON agent_context(agent_id, context_key);

