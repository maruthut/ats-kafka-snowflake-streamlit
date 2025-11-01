-- =====================================================================
-- Deploy Streamlit-in-Snowflake Dashboard for ATS Monitoring
-- =====================================================================
-- This script creates a Streamlit app inside Snowflake using Snowsight
-- Prerequisites: ATS_DB and views must already exist
-- =====================================================================

-- =====================================================================
-- PREREQUISITE: Grant Permissions (Run as ACCOUNTADMIN first)
-- =====================================================================
-- If you get "Insufficient privileges" error, run these grants first:
-- USE ROLE ACCOUNTADMIN;
-- GRANT CREATE STAGE ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE SYSADMIN;
-- GRANT CREATE STREAMLIT ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE SYSADMIN;
-- =====================================================================

USE ROLE SYSADMIN;
USE DATABASE ATS_DB;
USE SCHEMA ATS_SCHEMA;
USE WAREHOUSE COMPUTE_WH;

-- =====================================================================
-- Step 1: Create Stage for Streamlit App Files
-- =====================================================================

CREATE STAGE IF NOT EXISTS ATS_STREAMLIT_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for ATS Streamlit-in-Snowflake application files';

-- Verify stage creation
SHOW STAGES LIKE 'ATS_STREAMLIT_STAGE';

-- =====================================================================
-- Step 2: Upload Files to Stage (Manual Step)
-- =====================================================================
-- You need to upload these files using SnowSQL or Snowsight UI:
--
-- Files to upload:
-- 1. streamlit_app.py - Main dashboard application
-- 2. environment.yml - Python dependencies (NO Python version specified!)
--
-- ⚠️ IMPORTANT: environment.yml should NOT include python=X.X version
-- Let Snowflake manage the Python runtime automatically
-- Correct format:
--   dependencies:
--     - streamlit
--     - snowflake-snowpark-python
--     - pandas
--     - plotly
--
-- Option A - Using SnowSQL:
-- PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/streamlit_app.py @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/environment.yml @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
--
-- Option B - Using Snowsight UI (Recommended):
-- 1. Navigate to Data > Databases > ATS_DB > ATS_SCHEMA > Stages > ATS_STREAMLIT_STAGE
-- 2. Click "+ Files" button
-- 3. Upload streamlit_app.py and environment.yml
--

-- List files in stage to verify upload
LIST @ATS_STREAMLIT_STAGE;

-- Expected output:
-- name                                      | size  | md5  | last_modified
-- -------------------------------------------------------------------------
-- ATS_STREAMLIT_STAGE/streamlit_app.py     | ~12KB | ...  | ...
-- ATS_STREAMLIT_STAGE/environment.yml      | ~200B | ...  | ...

-- =====================================================================
-- Step 3: Create Streamlit App Object
-- =====================================================================

CREATE OR REPLACE STREAMLIT ATS_DASHBOARD_NATIVE
    ROOT_LOCATION = '@ATS_DB.ATS_SCHEMA.ATS_STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = COMPUTE_WH
    COMMENT = 'ATS Real-Time Monitoring Dashboard - Snowflake Native Version';

-- =====================================================================
-- Step 4: Grant Permissions
-- =====================================================================

-- Grant usage on database and schema
GRANT USAGE ON DATABASE ATS_DB TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA ATS_SCHEMA TO ROLE SYSADMIN;

-- Grant SELECT on all views used by the dashboard
GRANT SELECT ON VIEW ATS_DB.ATS_SCHEMA.ATS_TRANSFORMED TO ROLE SYSADMIN;
GRANT SELECT ON VIEW ATS_DB.ATS_SCHEMA.ATS_ALERTS TO ROLE SYSADMIN;
GRANT SELECT ON VIEW ATS_DB.ATS_SCHEMA.ATS_HOURLY_STATS TO ROLE SYSADMIN;
GRANT SELECT ON VIEW ATS_DB.ATS_SCHEMA.ATS_LATEST_STATUS TO ROLE SYSADMIN;

-- Grant usage on warehouse
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE SYSADMIN;

-- Grant usage on Streamlit app
GRANT USAGE ON STREAMLIT ATS_DB.ATS_SCHEMA.ATS_DASHBOARD_NATIVE TO ROLE SYSADMIN;

-- =====================================================================
-- Step 5: Verify Deployment
-- =====================================================================

-- Show created Streamlit app
SHOW STREAMLITS IN SCHEMA ATS_SCHEMA;

-- =====================================================================
-- Deployment Complete!
-- =====================================================================
-- To access your dashboard:
--
-- Method 1: Via Snowsight UI (Recommended)
-- 1. Open Snowsight: https://app.snowflake.com
-- 2. Navigate to: Streamlit tab (left sidebar)
-- 3. Find: ATS_DASHBOARD_NATIVE
-- 4. Click to launch the dashboard
--
-- Method 2: Via Direct Navigation
-- 1. In Snowsight, go to: Projects > Streamlit
-- 2. Click on ATS_DASHBOARD_NATIVE
--
-- Method 3: Via Worksheets
-- 1. In any SQL worksheet, you can see your Streamlit apps
-- 2. Right-click on ATS_DASHBOARD_NATIVE > Open in Streamlit
-- =====================================================================

-- =====================================================================
-- Optional: Share with Other Users
-- =====================================================================

-- Create a role for dashboard viewers (optional)
-- CREATE ROLE IF NOT EXISTS ATS_VIEWER;
-- GRANT USAGE ON DATABASE ATS_DB TO ROLE ATS_VIEWER;
-- GRANT USAGE ON SCHEMA ATS_SCHEMA TO ROLE ATS_VIEWER;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA ATS_SCHEMA TO ROLE ATS_VIEWER;
-- GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE ATS_VIEWER;
-- GRANT USAGE ON STREAMLIT ATS_DB.ATS_SCHEMA.ATS_DASHBOARD_NATIVE TO ROLE ATS_VIEWER;
-- GRANT ROLE ATS_VIEWER TO USER <username>;

-- =====================================================================
-- Troubleshooting
-- =====================================================================

-- Issue 1: "Insufficient privileges" error
-- Solution: Run grants as ACCOUNTADMIN (see PREREQUISITE section at top)

-- Issue 2: "Packages not found: python==X.X" error
-- Solution: Remove Python version from environment.yml
-- Let Snowflake manage Python runtime automatically
-- WRONG: dependencies: - python=3.9
-- RIGHT: dependencies: - streamlit (no Python version)

-- Issue 3: No data available in dashboard
-- Solution: Check if views exist and have data
SHOW VIEWS IN SCHEMA ATS_SCHEMA;
SELECT COUNT(*) FROM ATS_TRANSFORMED;  -- Should return > 0
SELECT COUNT(*) FROM ATS_ALERTS;       -- May be 0 if no alerts

-- Issue 4: Files not found in stage
-- Solution: Re-upload files
LIST @ATS_STREAMLIT_STAGE;
-- If missing, re-upload via Snowsight UI or SnowSQL

-- Issue 5: Dashboard shows errors after code changes
-- Solution: Drop and recreate Streamlit object
DROP STREAMLIT IF EXISTS ATS_DASHBOARD_NATIVE;
-- Then re-run Step 3 (CREATE STREAMLIT command)

-- Issue 6: Need to update dashboard code
-- Solution: Re-upload streamlit_app.py to stage (overwrites old version)
-- PUT file://path/to/streamlit_app.py @ATS_STREAMLIT_STAGE OVERWRITE=TRUE;
-- Changes are picked up automatically on next dashboard access

-- Check Streamlit app details
DESCRIBE STREAMLIT ATS_DASHBOARD_NATIVE;

-- View Streamlit app properties
SHOW STREAMLITS LIKE 'ATS_DASHBOARD_NATIVE';

-- =====================================================================
-- Architecture Notes
-- =====================================================================
-- 
-- Stage Storage:
-- - Files stay in @ATS_STREAMLIT_STAGE (internal Snowflake storage)
-- - Stage is persistent until explicitly deleted
-- - Files can be updated by re-uploading with OVERWRITE=TRUE
--
-- Streamlit Object:
-- - References the stage via ROOT_LOCATION
-- - Reads files from stage on every dashboard access
-- - Uses COMPUTE_WH for executing SQL queries
-- - Runs in Snowflake's managed Python environment
--
-- Updates:
-- - Code changes: Re-upload to stage, reload dashboard
-- - Major changes: Drop and recreate Streamlit object
-- - Permission changes: Run GRANT commands as needed
--
-- =====================================================================
