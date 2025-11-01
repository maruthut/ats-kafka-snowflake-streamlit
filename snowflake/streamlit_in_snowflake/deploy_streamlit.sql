-- =====================================================================
-- Deploy Streamlit-in-Snowflake Dashboard for ATS Monitoring
-- =====================================================================
-- This script creates a Streamlit app inside Snowflake using Snowsight
-- Prerequisites: ATS_DB and views must already exist
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
-- Option A - Using SnowSQL:
-- PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/streamlit_app.py @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/environment.yml @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
--
-- Option B - Using Snowsight UI:
-- 1. Navigate to Data > Databases > ATS_DB > ATS_SCHEMA > Stages > ATS_STREAMLIT_STAGE
-- 2. Click "+ Files" button
-- 3. Upload streamlit_app.py and environment.yml
--

-- List files in stage to verify upload
LIST @ATS_STREAMLIT_STAGE;

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

-- Get Streamlit app URL (for reference)
SELECT SYSTEM$GET_STREAMLIT_URL('ATS_DB.ATS_SCHEMA.ATS_DASHBOARD_NATIVE') AS STREAMLIT_URL;

-- =====================================================================
-- Deployment Complete!
-- =====================================================================
-- To access your dashboard:
-- 1. Open Snowsight (https://app.snowflake.com)
-- 2. Navigate to: Streamlit > ATS_DASHBOARD_NATIVE
-- 3. Click to launch the dashboard
--
-- Alternative: Use the URL from the query above
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

-- Check if views exist
SHOW VIEWS IN SCHEMA ATS_SCHEMA;

-- Test view access
-- SELECT COUNT(*) FROM ATS_TRANSFORMED;
-- SELECT COUNT(*) FROM ATS_ALERTS;

-- Check stage contents
-- LIST @ATS_STREAMLIT_STAGE;

-- Drop and recreate if needed
-- DROP STREAMLIT IF EXISTS ATS_DASHBOARD_NATIVE;
