# Snowflake Account Setup Guide

## Getting Your Snowflake Account Details

### Option 1: Free Trial Account
If you don't have a Snowflake account, sign up for free trial:
1. Visit: https://signup.snowflake.com/
2. Fill in details and select:
   - **Cloud Provider**: AWS (recommended) or Azure/GCP
   - **Region**: Choose closest to you (e.g., us-east-1, eu-west-1)
3. You'll receive account details via email

### Option 2: Existing Account
If you have an existing Snowflake account, gather these details:

## Required Information

### 1. Account Identifier
Your Snowflake account identifier format:
```
<account_locator>.<region>.<cloud>
```

**Examples:**
- `xy12345.us-east-1` (AWS)
- `ab67890.west-europe.azure` (Azure)
- `cd54321.us-central1.gcp` (GCP)

**How to find:**
- Check welcome email from Snowflake
- Or find in Snowflake URL: `https://xy12345.us-east-1.snowflakecomputing.com`
- Or run in Snowflake worksheet: `SELECT CURRENT_ACCOUNT()`

### 2. User Credentials
```
Username: <your_username>
Password: <your_password>
```

### 3. Warehouse
Default is `COMPUTE_WH` (comes with all accounts)

**To verify:**
```sql
SHOW WAREHOUSES;
```

### 4. Role
Default is `PUBLIC` or `ACCOUNTADMIN`

**To verify:**
```sql
SHOW ROLES;
SELECT CURRENT_ROLE();
```

## Step-by-Step Configuration

### 1. Log into Snowflake Web UI
Navigate to: `https://<your_account>.snowflakecomputing.com`

### 2. Create Dedicated User (Optional but Recommended)
```sql
USE ROLE ACCOUNTADMIN;

-- Create user
CREATE USER ats_pipeline_user
  PASSWORD = 'SecurePassword123!'
  DEFAULT_ROLE = PUBLIC
  DEFAULT_WAREHOUSE = COMPUTE_WH;

-- Grant permissions
GRANT ROLE PUBLIC TO USER ats_pipeline_user;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER ats_pipeline_user;
```

### 3. Generate RSA Key Pair for Kafka Connector

**Windows PowerShell:**
```powershell
cd c:\Maruthu\Projects\ats_snowflake_snowlit

# Generate private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# Display public key
Get-Content rsa_key.pub
```

### 4. Assign Public Key to Snowflake User

```sql
-- Copy content of rsa_key.pub (exclude BEGIN/END PUBLIC KEY lines)
-- Then run:
ALTER USER your_username SET RSA_PUBLIC_KEY='
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
';

-- Verify
DESC USER your_username;
```

### 5. Update .env File

**Windows:**
```powershell
# Copy template
Copy-Item .env.example .env

# Edit file
code .env
# Or
notepad .env
```

**Content:**
```env
# Your Snowflake Account (format: account.region)
SNOWFLAKE_ACCOUNT=xy12345.us-east-1

# Your username
SNOWFLAKE_USER=your_username

# Your password
SNOWFLAKE_PASSWORD=your_secure_password

# Warehouse (default: COMPUTE_WH)
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Database (will be created by schema.sql)
SNOWFLAKE_DATABASE=ATS_DB

# Schema (will be created by schema.sql)
SNOWFLAKE_SCHEMA=ATS_SCHEMA

# Role
SNOWFLAKE_ROLE=PUBLIC

# Private key content (copy entire content of rsa_key.p8)
SNOWFLAKE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----
```

### 6. Run Snowflake Schema Setup

In Snowflake Web UI, execute the contents of `snowflake/schema.sql`:

```sql
-- This will create:
-- ✓ Database: ATS_DB
-- ✓ Schema: ATS_SCHEMA
-- ✓ Table: ATS_RAW_JSON
-- ✓ Dynamic Table: ATS_TRANSFORMED
-- ✓ Views: ATS_LATEST_STATUS, ATS_ALERTS, ATS_HOURLY_STATS
```

### 7. Verify Setup

```sql
-- Check database
SHOW DATABASES LIKE 'ATS_DB';

-- Check schema
USE DATABASE ATS_DB;
SHOW SCHEMAS LIKE 'ATS_SCHEMA';

-- Check tables
USE SCHEMA ATS_SCHEMA;
SHOW TABLES;
SHOW DYNAMIC TABLES;
SHOW VIEWS;

-- Verify permissions
SHOW GRANTS TO USER your_username;
```

## Common Issues

### Issue 1: Can't Find Account Identifier
```sql
-- Run in Snowflake worksheet
SELECT CURRENT_ACCOUNT(), CURRENT_REGION();
```

### Issue 2: Insufficient Privileges
```sql
-- Grant necessary permissions
USE ROLE ACCOUNTADMIN;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE PUBLIC;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PUBLIC;
```

### Issue 3: RSA Key Not Recognized
- Ensure no extra spaces/newlines in public key
- Remove BEGIN/END PUBLIC KEY headers
- Key should be one continuous string

### Issue 4: Warehouse Not Available
```sql
-- Create a warehouse
CREATE WAREHOUSE COMPUTE_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE;
```

## Security Best Practices

1. **Never commit sensitive files:**
   - `.env` (excluded in .gitignore)
   - `rsa_key.p8` (private key)
   - `rsa_key.pub` (public key)

2. **Use strong passwords:**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols

3. **Enable MFA** (Multi-Factor Authentication):
   - Snowflake Web UI → Settings → Security

4. **Rotate keys regularly:**
   - Generate new RSA key pair every 90 days

5. **Use dedicated service accounts:**
   - Don't use personal accounts for automation

## Cost Optimization

### For Testing/Development:
```sql
-- Use smallest warehouse
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'X-SMALL';

-- Enable auto-suspend
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60; -- 1 minute

-- Monitor credit usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC;
```

### Estimated Costs (X-Small Warehouse):
- **Credit cost**: ~$2-4 per hour of compute
- **Free trial**: Includes $400 credits
- **This project**: ~2-3 credits per day for testing

## Next Steps

Once Snowflake is configured:
1. ✅ Update `.env` file with your credentials
2. ✅ Run `docker-compose up -d`
3. ✅ Register Kafka connector
4. ✅ Access dashboard at http://localhost:8501
5. ✅ Verify data is flowing through the pipeline

## Support Resources

- **Snowflake Documentation**: https://docs.snowflake.com/
- **Community Support**: https://community.snowflake.com/
- **Free Training**: https://learn.snowflake.com/
- **Trial Support**: support@snowflake.com
