# 🚆 ATS-Kafka-Snowflake-Streamlit ELT Pipeline

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-maruthut-181717?logo=github)](https://github.com/maruthut/ats-kafka-snowflake-streamlit)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-3.5-231F20?logo=apache-kafka)](https://kafka.apache.org/)
[![Snowflake](https://img.shields.io/badge/Snowflake-ELT-29B5E8?logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)

**Real-Time Data Engineering Portfolio Project**

[🚀 Quick Start](#-quick-start) • [📸 Live Dashboard](docs/DASHBOARD_SCREENSHOTS.md) • [🔧 Troubleshooting](TROUBLESHOOTING.md) • [🏗️ Architecture](#️-architecture)

</div>

A real-time data pipeline demonstrating **Automatic Train Supervision (ATS)** telemetry ingestion, processing, and visualization using modern data engineering best practices.

## 📋 Project Overview

This project showcases a complete **ELT (Extract, Load, Transform)** architecture that:

1. **Simulates** realistic train telemetry data (passengers, power consumption, alerts)
2. **Streams** data through Apache Kafka
3. **Ingests** into Snowflake using Kafka Connector with VARIANT columns
4. **Transforms** using Snowflake Dynamic Tables (near real-time)
5. **Visualizes** via an interactive Streamlit dashboard

## 📸 Live Dashboard Screenshots

**🎯 See the complete pipeline in action!** [View Detailed Screenshots →](docs/DASHBOARD_SCREENSHOTS.md)

<div align="center">

### Key Performance Indicators
*115 active trains | 59 avg passengers | 36 active alerts | 149.45 kW avg power*

### Real-Time Monitoring Dashboard
*Live telemetry streaming from Snowflake with auto-refresh*

### Active Alerts System
*High power draw alerts with real-time tracking*

### Analytics & Insights
*Passenger distribution | Power consumption trends | Hourly statistics*

**📊 Complete visual documentation:** [`docs/DASHBOARD_SCREENSHOTS.md`](docs/DASHBOARD_SCREENSHOTS.md)

</div>

> **Note:** To view screenshots with actual images, please save the dashboard screenshots from your browser and place them in the `docs/images/` directory following the naming convention in `DASHBOARD_SCREENSHOTS.md`.

### 🎯 Key Features

- ✅ **Real-time streaming pipeline** with 30-second telemetry intervals
- ✅ **ELT architecture** using Snowflake VARIANT columns for flexible JSON storage
- ✅ **Dynamic Tables** for automatic data transformation
- ✅ **Alert system** for overcrowding and high power consumption
- ✅ **Interactive dashboard** with auto-refresh capabilities
- ✅ **Fully containerized** with Docker Compose
- ✅ **Production-ready** with proper error handling and monitoring

## 🏗️ Architecture

### **Dual-Dashboard Architecture**

```mermaid
graph TB
    subgraph "Data Source"
        A[🚆 ATS Simulator<br/>Python Producer<br/>Docker Container]
    end
    
    subgraph "Message Broker"
        B[📨 Apache Kafka<br/>Confluent Platform 7.5.0<br/>Topic: ats_telemetry]
    end
    
    subgraph "Data Warehouse - Snowflake"
        C[💾 ATS_RAW_JSON<br/>VARIANT Column<br/>Schema-flexible JSON]
        D[🔄 ATS_TRANSFORMED<br/>Dynamic Table<br/>Auto-refresh 1 min]
        E[📊 Analytical Views<br/>ATS_ALERTS<br/>ATS_HOURLY_STATS<br/>ATS_LATEST_STATUS]
    end
    
    subgraph "Dashboard 1: External"
        F[🐳 Streamlit Dashboard<br/>Docker Container<br/>localhost:8501<br/>👥 Train Operators<br/>🔐 Password Auth]
    end
    
    subgraph "Dashboard 2: Native"
        G[🌨️ Streamlit-in-Snowflake<br/>Snowsight UI<br/>👥 Data Analysts<br/>🔐 Snowflake RBAC]
    end
    
    A -->|JSON Telemetry<br/>30-second intervals| B
    B -->|Kafka Connect 2.2.0<br/>RSA Authentication| C
    C -->|ELT Pattern<br/>Raw Ingestion| D
    D -->|Transform<br/>Extract Fields| E
    E -->|ODBC Query<br/>Password Auth| F
    E -->|Snowpark API<br/>Session Context| G
    
    style A fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style B fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style C fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style D fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style E fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style F fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style G fill:#e0f2f1,stroke:#004d40,stroke-width:2px
```

### **Data Flow**

1. **Simulate** → ATS Simulator generates realistic train telemetry (passengers, power, location)
2. **Stream** → Kafka receives JSON messages every 30 seconds with high reliability
3. **Ingest** → Snowflake Kafka Connector loads raw JSON into VARIANT column (ELT pattern)
4. **Transform** → Dynamic Tables automatically extract structured fields every minute
5. **Analyze** → Views provide analytical layers (alerts, statistics, status)
6. **Visualize** → Two dashboards serve different user personas:
   - **External**: Docker-based Streamlit for operational monitoring
   - **Native**: Snowflake-embedded Streamlit for data analysts

### **Key Architecture Decisions**

1. **ELT Pattern**: Raw JSON → Snowflake → Transform in warehouse
2. **VARIANT Columns**: Schema flexibility for evolving telemetry
3. **Dynamic Tables**: Automatic near real-time transformation (1-minute lag)
4. **Dual Dashboards**: Serve multiple user personas (operations + analytics)
5. **Kafka as Backbone**: Reliable, scalable message streaming with at-least-once delivery

## 📁 Project Structure

```
ats-kafka-snowflake-streamlit/
├── docker-compose.yml              # Orchestrates all services
├── test_pipeline.py                # Pipeline testing script
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
├── ats_simulator/                  # Telemetry simulator
│   ├── producer.py                 # Kafka producer
│   ├── Dockerfile
│   └── requirements.txt
│
├── kafka_connect/                  # Kafka-Snowflake integration
│   ├── snowflake_connector_config.json
│   └── register_connector.py       # Connector registration
│
├── snowflake/                      # Snowflake database objects
│   ├── schema.sql                  # Tables, views, dynamic tables
│   └── SETUP_INSTRUCTIONS.md
│
└── streamlit_dashboard/            # Web dashboard
    ├── app.py                      # Streamlit application
    ├── Dockerfile
    └── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (for Windows/Mac) or Docker Engine (Linux)
- **Snowflake account** (free trial available)
- **Git** (to clone the repository)
- **OpenSSL** (for generating RSA keys)

### Step 1: Clone the Repository

```bash
git clone https://github.com/maruthut/ats-kafka-snowflake-streamlit.git
cd ats-kafka-snowflake-streamlit
```

### Step 2: Set Up Snowflake

#### 2.1 Generate RSA Key Pair

On Windows (PowerShell):
```powershell
# Install OpenSSL if not present (use Chocolatey or download binaries)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

#### 2.2 Configure Snowflake User

1. Log in to your Snowflake account
2. Open a SQL worksheet
3. Copy the public key content (excluding headers):
   ```sql
   ALTER USER your_username SET RSA_PUBLIC_KEY='MIIBIjANBgkqh...';
   ```

#### 2.3 Create Database Objects

Execute the SQL in `snowflake/schema.sql` to create:
- Database: `ATS_DB`
- Schema: `ATS_SCHEMA`
- Tables, Dynamic Tables, and Views

See `snowflake/SETUP_INSTRUCTIONS.md` for detailed steps.

### Step 3: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your Snowflake credentials
# Use any text editor (VS Code, Notepad++, vim, etc.)
```

**Required variables:**
```env
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ATS_DB
SNOWFLAKE_SCHEMA=ATS_SCHEMA
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_PRIVATE_KEY=<content_of_rsa_key.p8>
```

**⚠️ IMPORTANT - Password with Special Characters:**
If your Snowflake password contains `$` character, you must escape it properly in `docker-compose.yml`:
- Use `$$` (double dollar sign) in the `.env` file: `SNOWFLAKE_PASSWORD=MyPass$$word123`
- In `docker-compose.yml`, use array format for environment variables:
  ```yaml
  environment:
    - SNOWFLAKE_PASSWORD=MyPass$$word123
  ```
- The `$$` will be interpreted as a single `$` inside the container
- See `docker-compose.yml` streamlit-dashboard section for working example

### Step 4: Start the Pipeline

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 5: Register Snowflake Connector

```bash
cd kafka_connect
python register_connector.py
```

### Step 6: Verify Pipeline

```bash
# Run automated tests
python test_pipeline.py
```

### Step 7: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8501
```

You should see the ATS Real-Time Monitoring Dashboard with live telemetry data!

## 🎨 Dual-Dashboard Architecture

This project implements **two dashboard deployment models** to demonstrate architectural versatility:

### 1️⃣ External Streamlit Dashboard (Docker-based)
📍 **Location:** `streamlit_dashboard/app.py`  
🌐 **Access:** `http://localhost:8501`  
👥 **Target Audience:** Operational users (train operators, management)

**Features:**
- Runs as Docker container
- External network access
- Password authentication
- Suitable for non-Snowflake users
- Real-time data via ODBC connection

### 2️⃣ Streamlit-in-Snowflake (Native)
📍 **Location:** `snowflake/streamlit_in_snowflake/`  
🌐 **Access:** Snowsight UI (`https://app.snowflake.com`)  
👥 **Target Audience:** Data analysts, data engineers

**Features:**
- Runs inside Snowflake (zero-latency)
- Automatic authentication via Snowflake session
- Inherits Snowflake RBAC for security
- No external infrastructure required
- Direct Snowpark data access

### 🆚 Comparison

| Aspect | External Dashboard | Snowflake Native |
|--------|-------------------|------------------|
| **Infrastructure** | Docker container | Fully managed by Snowflake |
| **Authentication** | Password/env vars | Snowflake session (automatic) |
| **Network Latency** | Yes (external connection) | No (in-region access) |
| **Security** | External credential mgmt | Inherits Snowflake RBAC |
| **Target Users** | Anyone with URL | Snowflake account users |
| **Deployment** | `docker-compose up` | SQL + file upload |
| **Cost** | Infrastructure costs | Warehouse compute only |

### 🚀 Deploy Snowflake Native Dashboard

**Quick Start:**
```bash
# 1. Upload files to Snowflake stage (using SnowSQL)
cd snowflake/streamlit_in_snowflake
snowsql -a your_account -u your_user
PUT file://streamlit_app.py @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

# 2. Create Streamlit app (execute SQL)
# See: snowflake/streamlit_in_snowflake/deploy_streamlit.sql

# 3. Access via Snowsight
# Navigate to: Streamlit > ATS_DASHBOARD_NATIVE
```

**📖 Full Documentation:** [`snowflake/streamlit_in_snowflake/README.md`](snowflake/streamlit_in_snowflake/README.md)

### 💡 Why Two Dashboards?

**Portfolio Differentiation:**
- ✅ Shows architectural decision-making skills
- ✅ Demonstrates Snowflake advanced features expertise
- ✅ Proves ability to serve multiple user personas
- ✅ Illustrates enterprise deployment patterns

**Interview Talking Point:**
> "I implemented dual dashboards to serve different personas: the external dashboard for operational monitoring by train operators, and the Snowflake-native version for data analysts who need zero-latency access within their existing Snowflake environment. This mirrors real-world enterprise architectures where you balance accessibility with security and performance."

## 📊 Dashboard Features

The Streamlit dashboard provides:

1. **KPI Metrics**
   - Active trains count
   - Average passenger load
   - Active alerts
   - Average power consumption

2. **Real-Time Charts**
   - Passenger count timeline
   - Power draw timeline
   - Speed distribution
   - Passenger distribution histogram

3. **Alert System**
   - Overcrowding alerts (>600 passengers)
   - High power draw alerts (>150 kW)

4. **Analytics**
   - Hourly statistics
   - Incident tracking
   - Train status overview

5. **Auto-Refresh**
   - Configurable refresh intervals
   - Real-time data updates

## 🔧 Troubleshooting

**📖 For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

### Quick Fixes

#### Dashboard: "Missing SNOWFLAKE_PASSWORD"
If password contains `$` character:
```yaml
# In docker-compose.yml, use array format with $$ escaping:
environment:
  - SNOWFLAKE_PASSWORD=MyPass$$Go  # $$ becomes $ in container
```

### Kafka Connector Issues

Check connector status:
```bash
curl http://localhost:8083/connectors/snowflake-sink-connector/status | jq .
```

Restart connector:
```bash
curl -X POST http://localhost:8083/connectors/snowflake-sink-connector/restart
```

### No Data in Snowflake

1. Verify ATS simulator is running:
   ```bash
   docker logs ats-simulator
   ```

2. Check Kafka topic:
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic ats_telemetry \
     --from-beginning
   ```

3. Verify connector status (see above)

### Dashboard Connection Issues

1. Check Snowflake credentials in `.env`
2. Verify network connectivity
3. Check dashboard logs:
   ```bash
   docker logs streamlit-dashboard
   ```
4. **"Missing SNOWFLAKE_PASSWORD" error**: 
   - If password contains `$`, ensure it's escaped with `$$` in both `.env` and `docker-compose.yml`
   - Use array format in docker-compose: `- SNOWFLAKE_PASSWORD=Pass$$word`
   - Verify password is set in container: `docker exec streamlit-dashboard env | grep SNOWFLAKE_PASSWORD`

## 🛠️ Development

### Running Locally (Without Docker)

#### ATS Simulator
```bash
cd ats_simulator
pip install -r requirements.txt
python producer.py
```

#### Streamlit Dashboard
```bash
cd streamlit_dashboard
pip install -r requirements.txt
streamlit run app.py
```

### Customization

- **Modify telemetry frequency**: Edit `time.sleep(30)` in `producer.py`
- **Adjust alert thresholds**: Update constants in `producer.py`
- **Change refresh rate**: Modify TARGET_LAG in `schema.sql`
- **Customize dashboard**: Edit `app.py` in `streamlit_dashboard/`

## 📈 ELT Architecture Explained

This project implements a modern **ELT (Extract, Load, Transform)** pattern:

### 1. Extract & Load
- Raw JSON data is loaded directly into Snowflake
- Uses VARIANT column type for schema flexibility
- No upfront schema definition required

### 2. Transform
- **Dynamic Tables** automatically refresh based on source changes
- Structured columns extracted using JSON path notation
- `TARGET_LAG = '1 minute'` ensures near real-time transformation

### 3. Benefits
- ✅ Fast ingestion (no transformation overhead)
- ✅ Schema evolution without pipeline changes
- ✅ Full data fidelity (raw data preserved)
- ✅ Leverages Snowflake's compute power

## 🔐 Security Best Practices

- ✅ Environment variables for sensitive data
- ✅ `.env` file excluded from version control
- ✅ RSA key-pair authentication for Kafka Connector
- ✅ Role-based access control in Snowflake
- ✅ Network isolation with Docker networks

**⚠️ Never commit `.env` or private keys to Git!**

## 🚢 Deployment Considerations

### Production Recommendations

1. **Kafka**: Use managed Kafka (Confluent Cloud, AWS MSK)
2. **Monitoring**: Add Prometheus + Grafana for metrics
3. **Logging**: Centralize logs with ELK stack
4. **Scaling**: Increase Kafka partitions and connector tasks
5. **Security**: Enable SSL/TLS and SASL authentication
6. **Backup**: Regular Snowflake time-travel snapshots

## 📚 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Simulator | Python 3.11 | Generate telemetry data |
| Message Broker | Apache Kafka 3.5 | Stream processing |
| Connector | Snowflake Kafka Connector 2.1 | Data ingestion |
| Data Warehouse | Snowflake | Storage & transformation |
| Visualization | Streamlit 1.31 | Interactive dashboard |
| Orchestration | Docker Compose | Container management |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Maruthu T**
- GitHub: [@maruthut](https://github.com/maruthut)
- LinkedIn: [linkedin.com/in/maruthut](https://www.linkedin.com/in/maruthut)
- Project Repository: [ats-kafka-snowflake-streamlit](https://github.com/maruthut/ats-kafka-snowflake-streamlit)

## 🙏 Acknowledgments

- Inspired by real-world transit monitoring systems
- Built to demonstrate modern data engineering practices
- Designed for educational and portfolio purposes

---

**⭐ If you find this project useful, please give it a star!**

## � Adding Dashboard Screenshots to Your Portfolio

To showcase your working dashboard with actual images:

### Step 1: Capture Screenshots
1. Open dashboard at `http://localhost:8501`
2. Take screenshots of each section:
   - Main dashboard with KPIs
   - Active alerts panel
   - Passenger count timeline
   - Power draw timeline
   - Distribution charts
   - Hourly statistics
   - Train status table

### Step 2: Save Images
Save screenshots in `docs/images/` with these names:
- `dashboard-header.png` - Top header and controls
- `kpi-metrics.png` - Key Performance Indicators
- `active-alerts.png` - Alert panel
- `passenger-timeline.png` - Passenger count over time
- `power-timeline.png` - Power consumption chart
- `passenger-distribution.png` - Histogram
- `speed-distribution.png` - Box plot
- `readings-per-hour.png` - Hourly bar chart
- `incidents-per-hour.png` - Incident trends
- `train-status-table.png` - Status overview table

### Step 3: Commit and Push
```bash
git add docs/images/*.png
git commit -m "Add dashboard screenshots for portfolio"
git push origin main
```

### Step 4: View on GitHub
Your complete documentation with screenshots will be visible at:
`https://github.com/maruthut/ats-kafka-snowflake-streamlit/blob/main/docs/DASHBOARD_SCREENSHOTS.md`

---

## 📞 Support

For questions or issues:
1. Check the [Troubleshooting](TROUBLESHOOTING.md) guide
2. Review [`docs/DASHBOARD_SCREENSHOTS.md`](docs/DASHBOARD_SCREENSHOTS.md) for visual reference
3. Check existing [GitHub Issues](https://github.com/maruthut/ats-kafka-snowflake-streamlit/issues)
4. Create a new issue with detailed information

---

## 🌟 Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/maruthut/ats-kafka-snowflake-streamlit)
![GitHub repo size](https://img.shields.io/github/repo-size/maruthut/ats-kafka-snowflake-streamlit)
![GitHub stars](https://img.shields.io/github/stars/maruthut/ats-kafka-snowflake-streamlit?style=social)

---

*Built with ❤️ for the data engineering community by [Maruthu T](https://github.com/maruthut)*
