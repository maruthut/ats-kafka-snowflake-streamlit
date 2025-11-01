# Snowflake Setup Instructions

Complete these steps **before** starting the Docker containers.

## 1. Create RSA Key Pair for Kafka Connector Authentication

The Snowflake Kafka Connector **requires** RSA key-pair authentication (password authentication is NOT supported).

### On Windows PowerShell or Linux/Mac Terminal:

```bash
# Generate 2048-bit RSA private key
openssl genrsa -out snowflake_key.pem 2048

# Extract public key
openssl rsa -in snowflake_key.pem -pubout -out snowflake_key.pub

# Convert private key to PKCS8 format (required by Kafka Connector)
openssl pkcs8 -topk8 -inform PEM -outform PEM -in snowflake_key.pem -out snowflake_key_pkcs8.pem -nocrypt
```

**Result**: You'll have 3 files:
- `snowflake_key.pem` - Original private key
- `snowflake_key.pub` - Public key (to assign to Snowflake user)
- `snowflake_key_pkcs8.pem` - PKCS8 private key (for Kafka Connector)

## 2. Assign Public Key to Snowflake User

### Extract Public Key Content:
Open `snowflake_key.pub` and copy the content **excluding** the header and footer lines:
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA... <-- Copy this part only
-----END PUBLIC KEY-----
```

### In Snowflake Worksheet:
```sql
-- Replace 'admin' with your actual Snowflake username
ALTER USER admin SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...';

-- Verify it's set
DESC USER admin;
```

## 3. Grant Necessary Privileges

```sql
-- Use SYSADMIN role (recommended for production)
USE ROLE SYSADMIN;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE SYSADMIN;

-- Grant database creation
GRANT CREATE DATABASE ON ACCOUNT TO ROLE SYSADMIN;
```

## 4. Run schema.sql to Create Database Objects

Execute the entire contents of `snowflake/schema.sql` in Snowflake worksheet.

This creates:
- Database: `ATS_DB`
- Schema: `ATS_SCHEMA`
- Table: `ATS_RAW_JSON` (with VARIANT columns)
- Dynamic Table: `ATS_TRANSFORMED` (auto-refreshes every 1 minute)
- Views: `ATS_LATEST_STATUS`, `ATS_ALERTS`, `ATS_HOURLY_STATS`

**⚠️ IMPORTANT**: After creating the table, grant INSERT permission:
```sql
GRANT INSERT ON TABLE ATS_DB.ATS_SCHEMA.ATS_RAW_JSON TO ROLE SYSADMIN;
```

## 5. Update .env File with Credentials

```bash
# Copy template
cp .env.example .env

# Edit .env with your actual values
```

### Required Configuration:

```env
# Use format: account_locator.region (e.g., vec76717.us-east-1)
# Find in Snowflake URL: https://app.snowflake.com/{region}/{account}/
SNOWFLAKE_ACCOUNT=your_account.region

SNOWFLAKE_USER=admin

# ⚠️ IMPORTANT: If password contains $ character, escape with $$
# Example: Password "MyPass$Go" should be "MyPass$$Go"
SNOWFLAKE_PASSWORD=your_password

SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ATS_DB
SNOWFLAKE_SCHEMA=ATS_SCHEMA
SNOWFLAKE_ROLE=SYSADMIN

# Paste content from snowflake_key_pkcs8.pem (single line, no headers)
SNOWFLAKE_PRIVATE_KEY=MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcw...
```

## 6. Update docker-compose.yml (If Password Contains $)

If your password contains `$` character, you **must** update `docker-compose.yml`:

```yaml
streamlit-dashboard:
  environment:
    # Use array format with $$ escaping
    - SNOWFLAKE_ACCOUNT=vec76717.us-east-1
    - SNOWFLAKE_USER=admin
    - SNOWFLAKE_PASSWORD=MyPass$$Go  # $$ becomes $ in container
    - SNOWFLAKE_WAREHOUSE=COMPUTE_WH
    - SNOWFLAKE_DATABASE=ATS_DB
    - SNOWFLAKE_SCHEMA=ATS_SCHEMA
    - SNOWFLAKE_ROLE=SYSADMIN
```

## 7. Verification Checklist

Before starting Docker containers, verify:

- ✅ RSA key pair generated (3 files)
- ✅ Public key assigned to Snowflake user
- ✅ schema.sql executed successfully
- ✅ INSERT permission granted on ATS_RAW_JSON
- ✅ .env file configured with correct values
- ✅ Password escaped with $$ if it contains $
- ✅ docker-compose.yml updated if password contains $

## Common Issues

### "Table does not exist or is not authorized"
**Solution**: Grant INSERT permission:
```sql
GRANT INSERT ON TABLE ATS_DB.ATS_SCHEMA.ATS_RAW_JSON TO ROLE SYSADMIN;
```

### "Invalid account identifier"
**Solution**: Use format `account_locator.region` from your Snowflake URL

### "Missing SNOWFLAKE_PASSWORD" in Dashboard
**Solution**: 
1. Check `.env` file has password with `$$` escaping if needed
2. Verify `docker-compose.yml` uses array format: `- SNOWFLAKE_PASSWORD=...`
3. Test: `docker exec streamlit-dashboard env | grep SNOWFLAKE_PASSWORD`

### "snowflake.private.key must be non-empty"
**Solution**: Kafka Connector requires RSA keys, NOT password authentication
