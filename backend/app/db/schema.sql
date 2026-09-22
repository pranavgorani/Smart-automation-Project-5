-- ==============================================================================
-- AIRFARE-X INDIA: Real-Time Airfare Price Intelligence & Index Platform
-- PostgreSQL / Supabase Schema DDL
-- Organization: MoSPI | Department: DIID | Theme: Smart Automation
-- ==============================================================================

-- 1. Routes Table
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    route_code VARCHAR(20) UNIQUE NOT NULL,
    city_pair VARCHAR(100) NOT NULL,
    passenger_weight NUMERIC(6, 4) NOT NULL DEFAULT 0.05,
    route_weight NUMERIC(6, 4) NOT NULL DEFAULT 0.05,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routes_code ON routes(route_code);

-- 2. Airlines Table
CREATE TABLE IF NOT EXISTS airlines (
    id SERIAL PRIMARY KEY,
    airline_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market_share NUMERIC(5, 2) DEFAULT 0.0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Sources Table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- LIVE_API, PERMITTED_WEB, MOCK, CSV_IMPORT, DGCA_REFERENCE
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, DEGRADED, INACTIVE, ERROR
    last_success TIMESTAMP WITH TIME ZONE,
    last_failure TIMESTAMP WITH TIME ZONE,
    request_count INTEGER NOT NULL DEFAULT 0,
    success_rate NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    compliance_status VARCHAR(50) NOT NULL DEFAULT 'COMPLIANT',
    robots_checked BOOLEAN NOT NULL DEFAULT TRUE,
    rate_limit_seconds INTEGER NOT NULL DEFAULT 5,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Collection Runs Table
CREATE TABLE IF NOT EXISTS collection_runs (
    id SERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL, -- SUCCESS, PARTIAL, FAILED
    records_collected INTEGER NOT NULL DEFAULT 0,
    records_processed INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,
    duration_seconds NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    error_message TEXT
);

-- 5. Airfare Quotes Table
CREATE TABLE IF NOT EXISTS airfare_quotes (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- LIVE_API, PERMITTED_WEB, MOCK, CSV_IMPORT
    source_reference VARCHAR(255),
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    route VARCHAR(20) NOT NULL,
    airline VARCHAR(100) NOT NULL,
    flight_number VARCHAR(50),
    departure_date DATE NOT NULL,
    departure_time VARCHAR(20),
    arrival_time VARCHAR(20),
    search_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    advance_purchase_days INTEGER NOT NULL, -- 1, 7, 15, 30, 45
    fare_class VARCHAR(50) DEFAULT 'Economy',
    fare_family VARCHAR(50) DEFAULT 'Standard',
    base_fare NUMERIC(10, 2) NOT NULL,
    taxes NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    user_development_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    convenience_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    other_charges NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    total_fare NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    availability INTEGER DEFAULT 9,
    stops INTEGER NOT NULL DEFAULT 0,
    refundability VARCHAR(50) DEFAULT 'Non-refundable',
    raw_hash VARCHAR(64) UNIQUE,
    data_quality_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    is_outlier BOOLEAN NOT NULL DEFAULT FALSE,
    outlier_method VARCHAR(50),
    outlier_score NUMERIC(6, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quotes_route ON airfare_quotes(route);
CREATE INDEX IF NOT EXISTS idx_quotes_search_ts ON airfare_quotes(search_timestamp);
CREATE INDEX IF NOT EXISTS idx_quotes_dep_date ON airfare_quotes(departure_date);
CREATE INDEX IF NOT EXISTS idx_quotes_advance ON airfare_quotes(advance_purchase_days);
CREATE INDEX IF NOT EXISTS idx_quotes_airline ON airfare_quotes(airline);

-- 6. Index Values Table (Aggregated APIx)
CREATE TABLE IF NOT EXISTS index_values (
    id SERIAL PRIMARY KEY,
    index_date DATE NOT NULL UNIQUE,
    index_value NUMERIC(8, 2) NOT NULL,
    daily_change NUMERIC(6, 2) DEFAULT 0.0,
    weekly_change NUMERIC(6, 2) DEFAULT 0.0,
    monthly_change NUMERIC(6, 2) DEFAULT 0.0,
    base_period DATE NOT NULL DEFAULT '2026-01-01',
    methodology_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    route_count INTEGER NOT NULL DEFAULT 13,
    observation_count INTEGER NOT NULL DEFAULT 0,
    confidence_score NUMERIC(5, 2) NOT NULL DEFAULT 95.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_index_date ON index_values(index_date);

-- 7. Route Index Table
CREATE TABLE IF NOT EXISTS route_index (
    id SERIAL PRIMARY KEY,
    index_date DATE NOT NULL,
    route VARCHAR(20) NOT NULL,
    index_value NUMERIC(8, 2) NOT NULL,
    median_fare NUMERIC(10, 2) NOT NULL,
    mean_fare NUMERIC(10, 2) NOT NULL,
    fare_change NUMERIC(6, 2) DEFAULT 0.0,
    weight NUMERIC(6, 4) NOT NULL,
    observation_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_date, route)
);

CREATE INDEX IF NOT EXISTS idx_route_index_dt_rt ON route_index(index_date, route);

-- 8. Data Quality Table
CREATE TABLE IF NOT EXISTS data_quality (
    id SERIAL PRIMARY KEY,
    run_id INTEGER,
    source VARCHAR(100) NOT NULL,
    records_collected INTEGER NOT NULL DEFAULT 0,
    records_valid INTEGER NOT NULL DEFAULT 0,
    records_rejected INTEGER NOT NULL DEFAULT 0,
    duplicates INTEGER NOT NULL DEFAULT 0,
    missing_values INTEGER NOT NULL DEFAULT 0,
    outliers INTEGER NOT NULL DEFAULT 0,
    completeness_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    validity_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    timeliness_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    uniqueness_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    consistency_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    quality_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. DGCA Reference Records Table
CREATE TABLE IF NOT EXISTS dgca_reference_records (
    id SERIAL PRIMARY KEY,
    month VARCHAR(10) NOT NULL,
    route VARCHAR(20) NOT NULL,
    airline VARCHAR(100) NOT NULL,
    passengers INTEGER NOT NULL,
    average_fare NUMERIC(10, 2) NOT NULL,
    fuel_surcharge NUMERIC(10, 2) DEFAULT 0.0,
    source VARCHAR(100) DEFAULT 'DGCA_MONTHLY',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month, route, airline)
);
