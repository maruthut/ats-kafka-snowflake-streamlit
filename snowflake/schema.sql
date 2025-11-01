-- ============================================================================
-- ATS (Automatic Train Supervision) Snowflake Schema
-- ============================================================================
-- This schema implements an ELT architecture using:
-- 1. Raw VARIANT column for flexible JSON ingestion
-- 2. Dynamic tables for near real-time transformation
-- 3. Views for structured data access
-- 4. Proper security with role-based access control
-- ============================================================================

-- Set up the environment
-- NOTE: Replace 'SYSADMIN' with appropriate role for your organization
-- NEVER use ACCOUNTADMIN for application workloads in production
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ATS_DB
    COMMENT = 'Database for Automatic Train Supervision telemetry data';

USE DATABASE ATS_DB;

-- Create schema
CREATE SCHEMA IF NOT EXISTS ATS_SCHEMA
    COMMENT = 'Schema for ATS raw and transformed telemetry data';

USE SCHEMA ATS_SCHEMA;

-- ============================================================================
-- 1. RAW DATA TABLE (Ingested by Kafka Connector)
-- ============================================================================
-- This table receives raw JSON data from Kafka
-- The Snowflake Kafka Connector automatically creates this table
-- but we define it here for clarity

CREATE TABLE IF NOT EXISTS ATS_RAW_JSON (
    RECORD_METADATA VARIANT,
    RECORD_CONTENT VARIANT
);

COMMENT ON TABLE ATS_RAW_JSON IS 'Raw telemetry data ingested from Kafka in JSON format';

-- ============================================================================
-- 2. DYNAMIC TABLE FOR TRANSFORMATION (ELT Pattern)
-- ============================================================================
-- Dynamic tables automatically refresh based on changes to source data
-- TARGET_LAG specifies maximum acceptable staleness
-- Added data quality filters and deduplication

CREATE OR REPLACE DYNAMIC TABLE ATS_TRANSFORMED
    TARGET_LAG = '1 minute'
    WAREHOUSE = COMPUTE_WH
    COMMENT = 'Transformed telemetry data with structured columns and data quality checks'
    AS
SELECT
    RECORD_CONTENT:timestamp::TIMESTAMP_NTZ AS timestamp,
    RECORD_CONTENT:train_id::STRING AS train_id,
    RECORD_CONTENT:passenger_count::INTEGER AS passenger_count,
    RECORD_CONTENT:total_weight_tons::FLOAT AS total_weight_tons,
    RECORD_CONTENT:power_draw_kw::FLOAT AS power_draw_kw,
    RECORD_CONTENT:speed_kmh::FLOAT AS speed_kmh,
    RECORD_CONTENT:location.latitude::FLOAT AS latitude,
    RECORD_CONTENT:location.longitude::FLOAT AS longitude,
    RECORD_CONTENT:alerts.overcrowding::BOOLEAN AS is_overcrowded,
    RECORD_CONTENT:alerts.high_power_draw::BOOLEAN AS is_high_power_draw,
    CURRENT_TIMESTAMP() AS processed_at
FROM ATS_RAW_JSON
WHERE RECORD_CONTENT IS NOT NULL
    -- Data quality filters
    AND RECORD_CONTENT:train_id IS NOT NULL
    AND RECORD_CONTENT:passenger_count IS NOT NULL
    AND RECORD_CONTENT:timestamp IS NOT NULL
    -- Ensure reasonable data ranges
    AND RECORD_CONTENT:passenger_count::INTEGER >= 0
    AND RECORD_CONTENT:passenger_count::INTEGER <= 1000
    AND RECORD_CONTENT:speed_kmh::FLOAT >= 0
    AND RECORD_CONTENT:speed_kmh::FLOAT <= 200
-- Use QUALIFY to deduplicate based on train_id and timestamp
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY RECORD_CONTENT:train_id, RECORD_CONTENT:timestamp 
    ORDER BY RECORD_METADATA:CreateTime DESC
) = 1;

-- ============================================================================
-- 3. ANALYTICAL VIEWS
-- ============================================================================

-- View: Latest telemetry for each train
CREATE OR REPLACE VIEW ATS_LATEST_STATUS AS
SELECT
    train_id,
    timestamp,
    passenger_count,
    total_weight_tons,
    power_draw_kw,
    speed_kmh,
    latitude,
    longitude,
    is_overcrowded,
    is_high_power_draw
FROM ATS_TRANSFORMED
QUALIFY ROW_NUMBER() OVER (PARTITION BY train_id ORDER BY timestamp DESC) = 1;

COMMENT ON VIEW ATS_LATEST_STATUS IS 'Latest telemetry status for each train';

-- View: Alert summary
CREATE OR REPLACE VIEW ATS_ALERTS AS
SELECT
    timestamp,
    train_id,
    CASE
        WHEN is_overcrowded THEN 'OVERCROWDING'
        WHEN is_high_power_draw THEN 'HIGH_POWER_DRAW'
    END AS alert_type,
    passenger_count,
    power_draw_kw,
    total_weight_tons
FROM ATS_TRANSFORMED
WHERE is_overcrowded = TRUE OR is_high_power_draw = TRUE
ORDER BY timestamp DESC;

COMMENT ON VIEW ATS_ALERTS IS 'All alert events (overcrowding and high power draw)';

-- View: Hourly aggregates
CREATE OR REPLACE VIEW ATS_HOURLY_STATS AS
SELECT
    DATE_TRUNC('HOUR', timestamp) AS hour,
    COUNT(*) AS total_readings,
    COUNT(DISTINCT train_id) AS unique_trains,
    AVG(passenger_count) AS avg_passenger_count,
    MAX(passenger_count) AS max_passenger_count,
    AVG(power_draw_kw) AS avg_power_draw_kw,
    MAX(power_draw_kw) AS max_power_draw_kw,
    SUM(CASE WHEN is_overcrowded THEN 1 ELSE 0 END) AS overcrowding_incidents,
    SUM(CASE WHEN is_high_power_draw THEN 1 ELSE 0 END) AS high_power_incidents
FROM ATS_TRANSFORMED
GROUP BY DATE_TRUNC('HOUR', timestamp)
ORDER BY hour DESC;

COMMENT ON VIEW ATS_HOURLY_STATS IS 'Hourly aggregated statistics for telemetry data';

-- ============================================================================
-- 4. PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Create clustering key for better query performance on time-based queries
ALTER TABLE ATS_RAW_JSON CLUSTER BY (TO_DATE(RECORD_CONTENT:timestamp::TIMESTAMP_NTZ));

-- Create search optimization for frequent filters
-- ALTER TABLE ATS_TRANSFORMED ADD SEARCH OPTIMIZATION ON EQUALITY(train_id);

-- Enable automatic clustering
ALTER TABLE ATS_RAW_JSON RESUME RECLUSTER;

-- ============================================================================
-- 5. DATA RETENTION POLICY (Optional)
-- ============================================================================

-- Keep raw data for 90 days
-- CREATE OR REPLACE TASK DELETE_OLD_RAW_DATA
--   WAREHOUSE = COMPUTE_WH
--   SCHEDULE = 'USING CRON 0 2 * * * UTC'
-- AS
--   DELETE FROM ATS_RAW_JSON
--   WHERE RECORD_CONTENT:timestamp::TIMESTAMP_NTZ < DATEADD(day, -90, CURRENT_TIMESTAMP());

-- ============================================================================
-- 6. GRANT PERMISSIONS (Principle of Least Privilege)
-- ============================================================================

-- Create application-specific roles for better security
-- CREATE ROLE IF NOT EXISTS ATS_WRITER;
-- CREATE ROLE IF NOT EXISTS ATS_READER;

-- Grant usage on database and schema to specific roles
GRANT USAGE ON DATABASE ATS_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;

-- Grant SELECT only (no INSERT/UPDATE/DELETE) for dashboard access
GRANT SELECT ON ALL TABLES IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON ALL DYNAMIC TABLES IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;

-- Grant future SELECT privileges for new objects
GRANT SELECT ON FUTURE TABLES IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON FUTURE DYNAMIC TABLES IN SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;

-- For Kafka Connector, grant INSERT on raw table
-- GRANT INSERT ON TABLE ATS_DB.ATS_SCHEMA.ATS_RAW_JSON TO ROLE ATS_WRITER;

-- ============================================================================
-- 7. VERIFICATION QUERIES
-- ============================================================================

-- Check raw data count
-- SELECT COUNT(*) AS raw_record_count FROM ATS_RAW_JSON;

-- Check transformed data
-- SELECT * FROM ATS_TRANSFORMED ORDER BY timestamp DESC LIMIT 10;

-- Check latest status
-- SELECT * FROM ATS_LATEST_STATUS;

-- Check alerts
-- SELECT * FROM ATS_ALERTS LIMIT 20;

-- Check hourly stats
-- SELECT * FROM ATS_HOURLY_STATS LIMIT 24;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. The Kafka connector will automatically populate ATS_RAW_JSON
-- 2. The dynamic table ATS_TRANSFORMED refreshes automatically
-- 3. Views provide different analytical perspectives
-- 4. Adjust TARGET_LAG based on your latency requirements
-- 5. Monitor warehouse usage for dynamic table refreshes
-- ============================================================================
