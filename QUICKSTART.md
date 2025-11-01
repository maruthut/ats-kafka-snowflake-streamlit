# 🚀 Quick Start Guide

This guide will get you up and running with the ATS pipeline in under 30 minutes.

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Python 3.7+ installed
- ✅ Snowflake account (free trial available)
- ✅ Git installed (optional, for GitHub push)

## Step-by-Step Setup

### 1️⃣ Snowflake Setup (10 minutes)

#### Generate RSA Keys

```bash
# Windows PowerShell
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# View public key (copy content without BEGIN/END lines)
cat rsa_key.pub
```

#### Configure Snowflake

Open Snowflake Web UI and run:

```sql
-- Assign public key to user (paste key content without headers)
ALTER USER your_username SET RSA_PUBLIC_KEY='MIIBIjANBgkqh...';

-- Grant permissions
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PUBLIC;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE PUBLIC;

-- Run all SQL from snowflake/schema.sql
```

See `SNOWFLAKE_SETUP.md` for detailed instructions.

### 2️⃣ Configure Environment (5 minutes)

```bash
# Copy template
cp .env.example .env

# Edit with your Snowflake credentials
# Windows: notepad .env
# Mac/Linux: nano .env
```

Fill in your details:
```env
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ATS_DB
SNOWFLAKE_SCHEMA=ATS_SCHEMA
SNOWFLAKE_ROLE=PUBLIC
```

### 3️⃣ Start Services (5 minutes)

```bash
# Start all Docker containers
docker-compose up -d

# Wait 60 seconds for services to initialize
# Windows PowerShell: Start-Sleep -Seconds 60
# Mac/Linux: sleep 60
```

### 4️⃣ Register Kafka Connector (2 minutes)

```bash
cd kafka_connect
python register_connector.py
```

### 5️⃣ Verify & Test (5 minutes)

```bash
# Run automated tests
python test_pipeline.py

# Access dashboard
# Open browser to: http://localhost:8501
```

## 🧪 Testing

### Check if Data is Flowing

```bash
# Check ATS simulator logs
docker-compose logs ats-simulator

# Check Kafka messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ats_telemetry \
  --from-beginning \
  --max-messages 5
```

### Verify in Snowflake

```sql
-- Check raw data
SELECT COUNT(*) FROM ATS_RAW_JSON;

-- View transformed data
SELECT * FROM ATS_TRANSFORMED ORDER BY timestamp DESC LIMIT 10;

-- Check alerts
SELECT * FROM ATS_ALERTS LIMIT 10;
```

## 📊 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit Dashboard | http://localhost:8501 | Main dashboard |
| Kafka Connect API | http://localhost:8083 | Connector status |

## 🔧 Troubleshooting

### Services Not Starting

```bash
# Check Docker is running
docker info

# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]
```

### No Data in Dashboard

1. **Check ATS simulator**: `docker-compose logs ats-simulator`
2. **Verify Kafka messages**: See "Check if Data is Flowing" above
3. **Check connector status**: `python test_pipeline.py`
4. **Verify Snowflake credentials**: Check `.env` file

### Port Conflicts

If ports 8501, 8083, 9092, or 9093 are in use:

```bash
# Windows: Find what's using the port
netstat -ano | findstr "8501"

# Mac/Linux
lsof -i :8501

# Stop conflicting process or edit docker-compose.yml to use different ports
```

## 🐛 Common Issues

### "Docker is not running"
- **Solution**: Start Docker Desktop

### "Connector registration failed"
- **Solution**: 
  1. Verify `.env` has correct Snowflake credentials
  2. Check RSA public key is assigned in Snowflake
  3. Wait 2 minutes and try again

### "No messages in Kafka"
- **Solution**:
  1. Check ATS simulator: `docker-compose logs ats-simulator`
  2. Restart simulator: `docker-compose restart ats-simulator`

## 🚀 Push to GitHub

```bash
# 1. Create a new repository on GitHub
#    Go to: https://github.com/new
#    Repository name: ats-kafka-snowflake-streamlit
#    Description: Real-time ATS telemetry pipeline with Kafka, Snowflake, and Streamlit
#    Make it Public (for portfolio)
#    Do NOT initialize with README

# 2. Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/ats-kafka-snowflake-streamlit.git
git push -u origin main
```

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything including volumes (careful!)
docker-compose down -v
```

## 📚 Additional Resources

- **README.md** - Complete project documentation
- **SNOWFLAKE_SETUP.md** - Detailed Snowflake configuration guide
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment checklist
- **PROJECT_SUMMARY.md** - Technical project summary

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Snowflake setup | 10 min |
| Environment config | 5 min |
| Start services | 5 min |
| Register connector | 2 min |
| Verify & test | 5 min |
| **Total** | **~30 min** |

## ✅ Success Checklist

- [ ] Docker Desktop is running
- [ ] Snowflake account configured
- [ ] `.env` file created with credentials
- [ ] All services started: `docker-compose ps`
- [ ] Connector registered: `python test_pipeline.py`
- [ ] Dashboard accessible: http://localhost:8501
- [ ] Data visible in Snowflake
- [ ] Git repository ready (optional)

---

**🎉 Congratulations! Your ATS pipeline is now running!**

For detailed documentation, see `README.md`
