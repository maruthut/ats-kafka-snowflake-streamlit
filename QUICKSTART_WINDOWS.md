# Quick Start Guide for Windows (Docker Desktop)

## Prerequisites Setup

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Enable WSL 2 backend (recommended)
   - Start Docker Desktop

2. **Install OpenSSL** (for RSA key generation)
   ```powershell
   # Using Chocolatey
   choco install openssl

   # Or download binaries from: https://slproweb.com/products/Win32OpenSSL.html
   ```

3. **Verify Installation**
   ```powershell
   docker --version
   docker-compose --version
   openssl version
   ```

## Setup Steps

### 1. Generate Snowflake RSA Keys

```powershell
# Navigate to project directory
cd c:\Maruthu\Projects\ats_snowflake_snowlit

# Generate private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# View public key (copy content without BEGIN/END lines)
Get-Content rsa_key.pub
```

### 2. Configure Snowflake

Open Snowflake Web UI and run:

```sql
-- Assign public key to user (paste key content without headers)
ALTER USER your_username SET RSA_PUBLIC_KEY='MIIBIjANBgkqh...';

-- Grant permissions
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PUBLIC;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE PUBLIC;

-- Run all SQL from snowflake/schema.sql
```

### 3. Create .env File

```powershell
# Copy template
Copy-Item .env.example .env

# Edit with your credentials (use notepad or VS Code)
notepad .env
```

Fill in your Snowflake details:
```env
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ATS_DB
SNOWFLAKE_SCHEMA=ATS_SCHEMA
SNOWFLAKE_ROLE=PUBLIC
```

### 4. Start Services

```powershell
# Start all containers
docker-compose up -d

# Wait 60 seconds for services to initialize
Start-Sleep -Seconds 60

# Check status
docker-compose ps

# View logs
docker-compose logs -f ats-simulator
```

### 5. Register Kafka Connector

```powershell
# Run PowerShell script
cd kafka_connect
.\register_connector.ps1

# Verify connector
Invoke-RestMethod -Uri "http://localhost:8083/connectors/snowflake-sink-connector/status" | ConvertTo-Json
```

### 6. Access Dashboard

Open browser: http://localhost:8501

## Testing Locally

### Test Kafka Producer

```powershell
# Check if messages are being produced
docker exec -it kafka kafka-console-consumer `
  --bootstrap-server localhost:9092 `
  --topic ats_telemetry `
  --from-beginning `
  --max-messages 5
```

### Test Snowflake Connection

In Snowflake Web UI:
```sql
-- Check raw data
SELECT COUNT(*) FROM ATS_RAW_JSON;

-- View transformed data
SELECT * FROM ATS_TRANSFORMED ORDER BY timestamp DESC LIMIT 10;

-- Check alerts
SELECT * FROM ATS_ALERTS LIMIT 10;
```

## Troubleshooting

### Docker Issues

```powershell
# Restart Docker Desktop
# Then restart containers
docker-compose down
docker-compose up -d
```

### Port Conflicts

```powershell
# Check what's using ports
netstat -ano | findstr "8501"
netstat -ano | findstr "9092"

# Stop conflicting processes or change ports in docker-compose.yml
```

### Clean Start

```powershell
# Remove all containers and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## Next Steps

1. ✅ Initialize Git repository
2. ✅ Create GitHub repository
3. ✅ Push code to GitHub
4. ✅ Test dashboard functionality
5. ✅ Add screenshots to README
6. ✅ Share portfolio link!

## Git Setup

```powershell
# Initialize repo
git init
git add .
git commit -m "Initial commit: ATS Kafka Snowflake Streamlit pipeline"

# Create GitHub repo (via web UI), then:
git remote add origin https://github.com/your-username/ats-kafka-snowflake-streamlit.git
git branch -M main
git push -u origin main
```

## Useful Commands

```powershell
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f ats-simulator

# Restart single service
docker-compose restart streamlit-dashboard

# Stop all
docker-compose stop

# Remove all
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Performance Tips

1. **Allocate more resources to Docker Desktop**
   - Settings → Resources → Advanced
   - Recommended: 4 GB RAM, 2 CPUs

2. **Use WSL 2 backend**
   - Better performance on Windows
   - Settings → General → Use WSL 2

3. **Optimize Snowflake warehouse**
   - Start with X-Small for testing
   - Scale up for production

## Support

If you encounter issues:
1. Check Docker Desktop is running
2. Verify .env file has correct credentials
3. Review logs: `docker-compose logs`
4. Ensure ports 8501, 8083, 9092, 9093 are available
