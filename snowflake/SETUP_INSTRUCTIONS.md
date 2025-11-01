# Setup instructions for Snowflake
# Run these commands in your Snowflake worksheet before starting the project

## 1. Create RSA key pair for Kafka Connector authentication
# On your local machine (Windows PowerShell):
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

## 2. Assign public key to Snowflake user
# In Snowflake worksheet:
ALTER USER your_username SET RSA_PUBLIC_KEY='<paste_public_key_content_without_headers>';

## 3. Grant necessary privileges
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PUBLIC;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE PUBLIC;
GRANT CREATE SCHEMA ON DATABASE ATS_DB TO ROLE PUBLIC;
GRANT CREATE TABLE ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT CREATE DYNAMIC TABLE ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;
GRANT CREATE VIEW ON SCHEMA ATS_DB.ATS_SCHEMA TO ROLE PUBLIC;

## 4. Run the schema.sql file to create all database objects
# Execute the contents of snowflake/schema.sql in Snowflake worksheet

## 5. Update .env file with your Snowflake credentials
# Copy .env.example to .env and fill in your actual values
