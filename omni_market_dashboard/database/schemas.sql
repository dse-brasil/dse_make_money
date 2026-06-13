-- ==========================================
-- RELATIONAL DATA MODEL (OLTP)
-- ==========================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    risk_profile VARCHAR(50) DEFAULT 'MODERATE', -- CONSERVATIVE, MODERATE, AGGRESSIVE
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Assets table (Universal Asset Registry)
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'BTC/USDT', 'PETR4', 'KNIP11', 'CDB_ITAU_120'
    name VARCHAR(150) NOT NULL,
    asset_class VARCHAR(50) NOT NULL, -- 'CRYPTO', 'B3_STOCK', 'FII', 'FIXED_INCOME', 'REAL_ESTATE'
    currency VARCHAR(10) DEFAULT 'BRL',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Fixed Income asset specifications
CREATE TABLE IF NOT EXISTS asset_details_fixed_income (
    asset_id INT PRIMARY KEY REFERENCES assets(id) ON DELETE CASCADE,
    issuer VARCHAR(100) NOT NULL,
    indexer_type VARCHAR(20) NOT NULL, -- 'CDI', 'IPCA', 'PRE', 'SELIC'
    indexer_multiplier NUMERIC(5, 2) DEFAULT 100.00, -- e.g., 120.00 representing 120% of CDI
    spread NUMERIC(5, 2) DEFAULT 0.00, -- e.g., 2.50 representing Indexer + 2.5%
    maturity_date DATE NOT NULL,
    minimum_investment NUMERIC(15, 2),
    liquidity_type VARCHAR(50) DEFAULT 'MATURITY', -- 'DAILY', 'MATURITY', '30_DAYS'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Physical Real Estate asset specifications
CREATE TABLE IF NOT EXISTS asset_details_real_estate (
    asset_id INT PRIMARY KEY REFERENCES assets(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    area_sqm NUMERIC(10, 2) NOT NULL,
    purchase_price NUMERIC(15, 2) NOT NULL,
    appraisal_value NUMERIC(15, 2),
    registration_number VARCHAR(100), -- Cartório de Registro de Imóveis (Matrícula)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Transactions Ledger (Immutable transactional history)
CREATE TABLE IF NOT EXISTS transactions_ledger (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolios(id) ON DELETE RESTRICT,
    asset_id INT REFERENCES assets(id) ON DELETE RESTRICT,
    type VARCHAR(30) NOT NULL, -- 'BUY', 'SELL', 'DIVIDEND', 'INTEREST', 'TAX', 'REBALANCING_TRANSFER'
    quantity NUMERIC(18, 8) NOT NULL,
    unit_price NUMERIC(18, 8) NOT NULL,
    total_amount NUMERIC(18, 2) NOT NULL, -- (quantity * unit_price) + fees
    fees NUMERIC(10, 2) DEFAULT 0.00,
    transaction_date TIMESTAMPTZ NOT NULL,
    hash_or_receipt VARCHAR(255), -- Transaction hash for web3/crypto or broker receipt ID
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance on relational schema
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio ON transactions_ledger(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_asset ON transactions_ledger(asset_id);
CREATE INDEX IF NOT EXISTS idx_assets_class ON assets(asset_class);


-- ==========================================
-- TIME-SERIES DATA MODEL (OLAP)
-- ==========================================

-- 7. High-frequency crypto tick data (Millisecond precision)
CREATE TABLE IF NOT EXISTS crypto_ticks (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(30) NOT NULL,
    price NUMERIC(18, 8) NOT NULL,
    volume NUMERIC(18, 8) NOT NULL,
    side VARCHAR(10) NOT NULL, -- 'BUY', 'SELL'
    exchange VARCHAR(50) NOT NULL -- 'Binance', 'Coinbase', 'dYdX'
);

-- Convert to hypertable if using TimescaleDB
-- SELECT create_hypertable('crypto_ticks', 'time');

-- 8. Macroeconomic curves and reference indexes (Daily updates)
CREATE TABLE IF NOT EXISTS macro_rates (
    time DATE NOT NULL,
    rate_code VARCHAR(30) NOT NULL, -- 'CDI_DAILY', 'SELIC_DAILY', 'IPCA_MONTHLY'
    value NUMERIC(10, 6) NOT NULL, -- Percentage value (e.g. 0.000382 for daily or 10.50 for annual rate)
    PRIMARY KEY (time, rate_code)
);

-- 9. Daily Portfolio Balance / Net Asset Value (NAV) Snapshot
CREATE TABLE IF NOT EXISTS daily_portfolio_equity (
    time DATE NOT NULL,
    portfolio_id INT REFERENCES portfolios(id) ON DELETE CASCADE,
    total_equity NUMERIC(18, 2) NOT NULL,
    cash_allocation NUMERIC(18, 2) NOT NULL,  -- Treasury (CDBs)
    risk_allocation NUMERIC(18, 2) NOT NULL,  -- Trade (B3/Crypto) + FIIs/Real Estate
    PRIMARY KEY (time, portfolio_id)
);
