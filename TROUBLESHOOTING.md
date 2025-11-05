# 🔧 Troubleshooting Guide

Quick solutions to common issues encountered during deployment and testing.

---

## 🚨 Dashboard: "Missing SNOWFLAKE_PASSWORD" Error

### Symptoms
- Streamlit dashboard shows error: `Missing required environment variables: SNOWFLAKE_PASSWORD`
- Dashboard logs show: `ERROR - Missing required environment variables: SNOWFLAKE_PASSWORD`
- Container appears healthy but can't connect to Snowflake

### Root Cause
If your Snowflake password contains special characters like `$`, Docker Compose interprets them as variable substitution.

**Example:** Password `MyPass$Go` → Docker Compose tries to substitute `$Go` as a variable → Result: Empty password

### Solution

#### Step 1: Update `.env` file
```env
# Use $$ (double dollar sign) to escape $ character
SNOWFLAKE_PASSWORD=YourPassword$$Here
```

#### Step 2: Update `docker-compose.yml`
```yaml
streamlit-dashboard:
  environment:
    # Use array format (- KEY=VALUE) instead of mapping format
    - SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT}
    - SNOWFLAKE_USER=${SNOWFLAKE_USER}
    - SNOWFLAKE_PASSWORD=${SNOWFLAKE_PASSWORD}  # Read from .env file
    - SNOWFLAKE_WAREHOUSE=${SNOWFLAKE_WAREHOUSE}
    - SNOWFLAKE_DATABASE=${SNOWFLAKE_DATABASE}
    - SNOWFLAKE_SCHEMA=${SNOWFLAKE_SCHEMA}
    - SNOWFLAKE_ROLE=${SNOWFLAKE_ROLE}
```

#### Step 3: Restart Dashboard
```bash
docker-compose restart streamlit-dashboard
```

#### Step 4: Verify Password is Set
```bash
# Check environment variable inside container
docker exec streamlit-dashboard env | grep SNOWFLAKE_PASSWORD

# Expected output (single $ character if you used $$):
SNOWFLAKE_PASSWORD=YourPassword$Here
```

#### Step 5: Check Dashboard Logs
```bash
docker-compose logs streamlit-dashboard

# Look for:
# ✅ "Snowflake connection established successfully"
# ✅ "Number of results in first chunk: X"
```

### Why This Works
- `$$` in Docker Compose YAML escapes to single `$` inside container
- Array format (`- KEY=VALUE`) prevents YAML parsing issues with special characters
- Single `$` is the actual password character expected by Snowflake

---

## 🔌 Kafka Connect: "Table does not exist or is not authorized"

### Symptoms
- Connector status shows task state: `FAILED`
- Logs show: `HTTP Status 400 - The supplied table does not exist or is not authorized`
- No data appearing in Snowflake

### Root Cause
Missing INSERT permission on Snowflake table for the SYSADMIN role.

### Solution
```sql
-- In Snowflake worksheet:
USE ROLE ACCOUNTADMIN;
GRANT INSERT ON TABLE ATS_DB.ATS_SCHEMA.ATS_RAW_JSON TO ROLE SYSADMIN;
```

### Verify Fix
```bash
# Delete and re-register connector
curl -X DELETE http://localhost:8083/connectors/snowflake-sink-connector
python kafka_connect/register_connector.py

# Check status (should show RUNNING)
curl http://localhost:8083/connectors/snowflake-sink-connector/status | jq .
```

---

## 🔑 Kafka Connect: "snowflake.private.key must be non-empty"

### Symptoms
- Connector registration fails
- Error: `snowflake.private.key must be non-empty`
- Attempted to use password authentication

### Root Cause
**Snowflake Kafka Connector does NOT support password authentication.** It requires RSA key-pair authentication only.

### Solution

#### Generate RSA Key Pair
```bash
# Generate private key
openssl genrsa -out snowflake_key.pem 2048

# Extract public key
openssl rsa -in snowflake_key.pem -pubout -out snowflake_key.pub

# Convert to PKCS8 format (required by Kafka Connector)
openssl pkcs8 -topk8 -inform PEM -outform PEM -in snowflake_key.pem -out snowflake_key_pkcs8.pem -nocrypt
```

#### Assign Public Key to Snowflake User
```sql
-- Extract content from snowflake_key.pub (exclude headers)
ALTER USER admin SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...';
```

#### Update `.env` File
```env
# Paste PKCS8 private key content (single line, no headers)
SNOWFLAKE_PRIVATE_KEY=MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcw...
```

#### Re-register Connector
```bash
python kafka_connect/register_connector.py
```

---

## 🌐 Kafka Connect: "Invalid Snowflake account identifier"

### Symptoms
- Error: `snowflake.url.name is not a valid snowflake url`
- Connector registration fails immediately

### Root Cause
Incorrect Snowflake account format. The account identifier must include region.

### Solution

#### Find Correct Account Format
From your Snowflake URL: `https://app.snowflake.com/{region}/{account}/`

**Example:**
- URL: `https://app.snowflake.com/us-east-1/abc12345/`
- **Correct format:** `abc12345.us-east-1`
- ❌ **Wrong:** `ORGNAME-ACCTNAME` (organization/account combo)

#### Update `.env`
```env
SNOWFLAKE_ACCOUNT=your_account.your_region
```

---

## 📊 No Data in Snowflake

### Symptoms
- Connector shows `RUNNING` status
- No rows in `ATS_RAW_JSON` table
- Query returns: `query produced no result`

### Possible Causes & Solutions

#### 1. Buffer Not Yet Flushed
**Cause:** Kafka Connector has `buffer.flush.time=60` seconds

**Solution:** Wait 60 seconds for initial data flush
```bash
# Wait for buffer flush
Start-Sleep -Seconds 60

# Check Snowflake
SELECT COUNT(*) FROM ATS_DB.ATS_SCHEMA.ATS_RAW_JSON;
```

#### 2. ATS Simulator Not Running
**Check:**
```bash
docker-compose ps ats-simulator

# Should show: Up
```

**Fix:**
```bash
docker-compose restart ats-simulator
docker-compose logs -f ats-simulator
```

#### 3. Kafka Topic Empty
**Check:**
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ats_telemetry \
  --from-beginning \
  --max-messages 5
```

**Expected:** JSON messages with train telemetry

---

## 🚂 Dashboard Shows "No Data Available"

### Symptoms
- Dashboard loads but shows: `No data available`
- Connection to Snowflake is successful
- Tables exist in Snowflake

### Possible Causes

#### 1. No Data in Last 24 Hours
Dashboard queries filter by: `timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())`

**Check:**
```sql
-- Check if data exists (any timeframe)
SELECT COUNT(*), MIN(timestamp), MAX(timestamp) 
FROM ATS_DB.ATS_SCHEMA.ATS_RAW_JSON;

-- If data is older than 24 hours, wait for new data from simulator
```

#### 2. Dynamic Table Not Refreshing
**Check:**
```sql
-- Verify Dynamic Table status
SHOW DYNAMIC TABLES IN SCHEMA ATS_DB.ATS_SCHEMA;

-- Check row count
SELECT COUNT(*) FROM ATS_DB.ATS_SCHEMA.ATS_TRANSFORMED;
```

**Fix:**
```sql
-- Manually refresh Dynamic Table
ALTER DYNAMIC TABLE ATS_DB.ATS_SCHEMA.ATS_TRANSFORMED REFRESH;
```

---

## 🐳 Container Health Checks Failing

### Check Container Status
```bash
docker-compose ps

# Look for "(unhealthy)" status
```

### View Health Check Logs
```bash
# Kafka
docker inspect kafka --format='{{json .State.Health}}' | jq .

# Kafka Connect
docker inspect kafka-connect --format='{{json .State.Health}}' | jq .

# ATS Simulator
docker inspect ats-simulator --format='{{json .State.Health}}' | jq .
```

### Common Fixes

#### Kafka Not Ready
```bash
# Wait for Kafka to fully start (can take 30-60 seconds)
docker-compose logs -f kafka

# Look for: "Kafka Server started"
```

#### Kafka Connect Plugin Missing
```bash
# Verify Snowflake connector installed
curl http://localhost:8083/connector-plugins | jq .

# Look for: "com.snowflake.kafka.connector.SnowflakeSinkConnector"
```

---

## 🔍 Debugging Checklist

Use this checklist to systematically debug issues:

### 1. Container Health
```bash
docker-compose ps
# All containers should show "Up" and "(healthy)" if applicable
```

### 2. Environment Variables
```bash
# Check .env file exists and has correct values
cat .env

# Verify variables in container
docker exec streamlit-dashboard env | grep SNOWFLAKE
docker exec kafka-connect env | grep SNOWFLAKE
```

### 3. Snowflake Objects
```sql
-- Verify database structure
USE DATABASE ATS_DB;
SHOW TABLES IN SCHEMA ATS_SCHEMA;
SHOW DYNAMIC TABLES IN SCHEMA ATS_SCHEMA;
SHOW VIEWS IN SCHEMA ATS_SCHEMA;
```

### 4. Data Flow
```bash
# 1. Check producer
docker-compose logs --tail=20 ats-simulator

# 2. Check Kafka topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ats_telemetry --max-messages 1

# 3. Check connector status
curl http://localhost:8083/connectors/snowflake-sink-connector/status | jq .

# 4. Check Snowflake data
# Run in Snowflake worksheet:
SELECT COUNT(*) FROM ATS_RAW_JSON;
```

### 5. Dashboard
```bash
# Check logs
docker-compose logs --tail=30 streamlit-dashboard

# Access dashboard
# Open browser: http://localhost:8501
```

---

## 📞 Still Having Issues?

### Collect Diagnostic Information
```bash
# 1. Container status
docker-compose ps > diagnostics.txt

# 2. All logs
docker-compose logs > full-logs.txt

# 3. Connector status
curl http://localhost:8083/connectors/snowflake-sink-connector/status >> diagnostics.txt

# 4. Environment check
docker exec streamlit-dashboard env | grep SNOWFLAKE >> diagnostics.txt
```

### Common Commands
```bash
# Restart everything
docker-compose down
docker-compose up -d

# Clean restart (removes volumes)
docker-compose down -v
docker-compose up -d

# View specific service logs
docker-compose logs -f [service-name]

# Execute command in container
docker exec -it [container-name] bash
```

### Useful Snowflake Queries
```sql
-- Check recent data
SELECT * FROM ATS_RAW_JSON ORDER BY RECORD_METADATA:CreateTime DESC LIMIT 10;

-- Check transformation
SELECT * FROM ATS_TRANSFORMED ORDER BY timestamp DESC LIMIT 10;

-- Check alerts
SELECT * FROM ATS_ALERTS WHERE timestamp >= DATEADD(hour, -1, CURRENT_TIMESTAMP());

-- Verify Dynamic Table freshness
SHOW DYNAMIC TABLES IN SCHEMA ATS_SCHEMA;
```

---

**📚 For detailed setup instructions, see:**
- `README.md` - Complete setup guide
- `snowflake/SETUP_INSTRUCTIONS.md` - Snowflake configuration
- `ARCHITECTURAL_REVIEW.md` - Code improvements and best practices
