# 🌨️ ATS Dashboard - Streamlit-in-Snowflake (Native)

## 📋 Overview

This is the **Snowflake-native version** of the ATS Real-Time Monitoring Dashboard. Unlike the external Docker-based dashboard, this runs entirely inside Snowflake using Streamlit-in-Snowflake (SiS).

### 🎯 Key Differences from External Dashboard

| Feature | External Dashboard | Streamlit-in-Snowflake |
|---------|-------------------|------------------------|
| **Deployment** | Docker container | Native Snowflake object |
| **Authentication** | Password/config file | Snowflake session (automatic) |
| **Data Access** | Network connection | Direct internal access |
| **Performance** | Network latency | Zero-latency (in-region) |
| **Security** | External credential management | Inherits Snowflake RBAC |
| **Audience** | External users (operators, managers) | Snowflake users (analysts, data engineers) |
| **Maintenance** | Infrastructure required | Fully managed by Snowflake |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│            Snowflake Account (Your Account)         │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │           ATS_DB Database                    │  │
│  │                                              │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │  ATS_SCHEMA                            │ │  │
│  │  │                                        │ │  │
│  │  │  📊 Views:                             │ │  │
│  │  │    • ATS_TRANSFORMED                   │ │  │
│  │  │    • ATS_ALERTS                        │ │  │
│  │  │    • ATS_HOURLY_STATS                  │ │  │
│  │  │    • ATS_LATEST_STATUS                 │ │  │
│  │  │                                        │ │  │
│  │  │  📦 Stage:                             │ │  │
│  │  │    • ATS_STREAMLIT_STAGE               │ │  │
│  │  │      - streamlit_app.py                │ │  │
│  │  │      - environment.yml                 │ │  │
│  │  │                                        │ │  │
│  │  │  🎨 Streamlit App:                     │ │  │
│  │  │    • ATS_DASHBOARD_NATIVE              │ │  │
│  │  │      (Snowpark-powered dashboard)      │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  🔧 Warehouse: COMPUTE_WH                          │
│  👤 Role: SYSADMIN                                 │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Files in This Directory

```
streamlit_in_snowflake/
├── streamlit_app.py          # Main Streamlit application (Snowpark version)
├── environment.yml            # Python dependencies for Snowflake
├── deploy_streamlit.sql       # SQL script to deploy to Snowflake
└── README.md                  # This file
```

---

## 🚀 Deployment Instructions

### Prerequisites

✅ ATS database and views already created (from `snowflake/schema.sql`)  
✅ Data flowing from Kafka to Snowflake  
✅ Snowflake account with Standard edition or higher  
✅ SYSADMIN role access  

### Step 1: Upload Files to Snowflake Stage

**Option A: Using SnowSQL (Recommended)**

```bash
# Connect to Snowflake
snowsql -a your_account.your_region -u your_username

# Execute deployment SQL (creates stage)
USE ROLE SYSADMIN;
USE DATABASE ATS_DB;
USE SCHEMA ATS_SCHEMA;

CREATE STAGE IF NOT EXISTS ATS_STREAMLIT_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for ATS Streamlit-in-Snowflake application files';

# Upload files (from your local machine)
PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/streamlit_app.py @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://c:/Maruthu/Projects/ats_snowflake_snowlit/snowflake/streamlit_in_snowflake/environment.yml @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

# Verify upload
LIST @ATS_STREAMLIT_STAGE;
```

**Option B: Using Snowsight UI**

1. Open Snowsight: https://app.snowflake.com
2. Navigate to: **Data** → **Databases** → **ATS_DB** → **ATS_SCHEMA** → **Stages**
3. Execute the `CREATE STAGE` command from `deploy_streamlit.sql`
4. Click on **ATS_STREAMLIT_STAGE**
5. Click **"+ Files"** button
6. Upload both files:
   - `streamlit_app.py`
   - `environment.yml`

### Step 2: Create Streamlit App

Execute the rest of `deploy_streamlit.sql` in Snowsight:

```sql
-- Create Streamlit app
CREATE OR REPLACE STREAMLIT ATS_DASHBOARD_NATIVE
    ROOT_LOCATION = '@ATS_DB.ATS_SCHEMA.ATS_STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = COMPUTE_WH
    COMMENT = 'ATS Real-Time Monitoring Dashboard - Snowflake Native Version';

-- Grant permissions
GRANT USAGE ON STREAMLIT ATS_DB.ATS_SCHEMA.ATS_DASHBOARD_NATIVE TO ROLE SYSADMIN;

-- Verify deployment
SHOW STREAMLITS IN SCHEMA ATS_SCHEMA;
```

### Step 3: Access Your Dashboard

**Via Snowsight UI (Recommended):**

1. Open Snowsight: https://app.snowflake.com
2. Navigate to **Streamlit** tab (left sidebar)
3. Find and click: **ATS_DASHBOARD_NATIVE**
4. Dashboard will open in a new panel

**Alternative Access Methods:**

- **From Projects Menu:** Projects → Streamlit → ATS_DASHBOARD_NATIVE
- **From Database Objects:** Navigate to ATS_DB → ATS_SCHEMA → Streamlit Apps → ATS_DASHBOARD_NATIVE → Right-click → Open in Streamlit

---

## 🎨 Dashboard Features

### Key Metrics (Same as External Dashboard)
- **Active Trains**: Real-time count of trains online
- **Avg Passengers**: Average passenger count per train
- **Active Alerts**: Number of overcrowding/high-power alerts
- **Avg Power Draw**: Current average power consumption

### Visualizations
1. **Passenger Count Timeline** - Line chart by train
2. **Power Draw Timeline** - Line chart with threshold indicator
3. **Passenger Distribution** - Histogram of passenger counts
4. **Train Speed Distribution** - Box plot by train
5. **Hourly Statistics** - Bar chart of readings per hour
6. **Incident Timeline** - Line chart of overcrowding/power incidents
7. **Train Status Table** - Real-time status of all trains

### Interactive Controls
- ✅ Auto-refresh toggle
- ⏱️ Refresh interval slider (10-60 seconds)
- 📊 Data points slider (50-500 records)
- 🔄 Manual refresh button
- 🔍 Raw data explorer

---

## 🔧 Configuration

### Database Connection
- **Method**: Automatic via `get_active_session()`
- **No credentials needed** - uses Snowflake session context
- **Security**: Inherits user's Snowflake roles and permissions

### Python Dependencies
Specified in `environment.yml`:
- `streamlit=1.31.0` - Dashboard framework
- `snowflake-snowpark-python` - Snowflake data access
- `pandas` - Data manipulation
- `plotly` - Interactive charts

### Query Performance
- **Cache TTL**: 60 seconds (reduces warehouse usage)
- **Max Data Points**: 500 (prevents memory issues)
- **Default Limit**: 100 records
- **Query Timeout**: 30 seconds

---

## 🆚 When to Use This vs External Dashboard

### Use Streamlit-in-Snowflake When:
✅ Users already have Snowflake accounts  
✅ You want zero external infrastructure  
✅ Security/compliance requires data to stay in Snowflake  
✅ Target audience is data analysts/engineers  
✅ You want to leverage Snowflake RBAC for access control  

### Use External Dashboard When:
✅ Users don't have Snowflake accounts  
✅ Need public-facing or embedded dashboard  
✅ Target audience is operational staff (train operators, managers)  
✅ Want to integrate with external systems  
✅ Need custom authentication/authorization  

### Use BOTH When:
🎯 **Portfolio showcase** - Demonstrates architectural versatility  
🎯 **Multi-persona solution** - Serve different user types  
🎯 **Maximum impact** - Shows Snowflake expertise + cloud-native skills  

---

## 🐛 Troubleshooting

### Issue: "Streamlit app not found"
**Solution:**
```sql
-- Check if app exists
SHOW STREAMLITS IN SCHEMA ATS_SCHEMA;

-- Recreate if needed
DROP STREAMLIT IF EXISTS ATS_DASHBOARD_NATIVE;
-- Then re-run CREATE STREAMLIT command
```

### Issue: "No data available"
**Solution:**
1. Verify views exist:
   ```sql
   SHOW VIEWS IN SCHEMA ATS_SCHEMA;
   ```
2. Check if data is flowing:
   ```sql
   SELECT COUNT(*) FROM ATS_TRANSFORMED;
   SELECT COUNT(*) FROM ATS_ALERTS;
   ```
3. Ensure Kafka pipeline is running (see main README)

### Issue: "Permission denied" errors
**Solution:**
```sql
-- Grant required permissions
GRANT SELECT ON ALL VIEWS IN SCHEMA ATS_SCHEMA TO ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE SYSADMIN;
GRANT USAGE ON STREAMLIT ATS_DASHBOARD_NATIVE TO ROLE SYSADMIN;
```

### Issue: Files not uploading to stage
**Solution:**
1. Check stage exists:
   ```sql
   SHOW STAGES LIKE 'ATS_STREAMLIT_STAGE';
   ```
2. Verify permissions:
   ```sql
   GRANT READ, WRITE ON STAGE ATS_STREAMLIT_STAGE TO ROLE SYSADMIN;
   ```
3. Use absolute file paths in PUT command

---

## 🔄 Updating the Dashboard

To update the dashboard after making changes:

```sql
-- 1. Upload new version
PUT file://c:/path/to/streamlit_app.py @ATS_STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- 2. Refresh the Streamlit app (if needed)
-- Just reload the dashboard in Snowsight - changes are picked up automatically

-- OR recreate the app
DROP STREAMLIT ATS_DASHBOARD_NATIVE;
CREATE STREAMLIT ATS_DASHBOARD_NATIVE
    ROOT_LOCATION = '@ATS_DB.ATS_SCHEMA.ATS_STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = COMPUTE_WH;
```

---

## 📊 Cost Optimization

### Warehouse Usage
- Dashboard queries use **COMPUTE_WH** (adjust size as needed)
- **Auto-suspend** recommended: 5 minutes of inactivity
- **Caching** reduces warehouse usage (60-second TTL)

### Recommended Settings
```sql
-- Optimize warehouse for dashboard workload
ALTER WAREHOUSE COMPUTE_WH SET
    WAREHOUSE_SIZE = 'X-SMALL'       -- Start small, scale if needed
    AUTO_SUSPEND = 300                -- 5 minutes
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
```

---

## 👨‍💼 Portfolio Talking Points

**Interview Question:** *"Why did you create two dashboards?"*

**Your Answer:**
> "I implemented a **dual-dashboard architecture** to demonstrate versatility and real-world thinking:
> 
> 1. **External Streamlit Dashboard** - For operational monitoring by non-Snowflake users (train operators, management teams). Runs in Docker, accessible via web browser.
> 
> 2. **Streamlit-in-Snowflake** - For data analysts and engineers who work inside Snowflake. Zero network latency, inherits Snowflake's security model, no external infrastructure.
> 
> This mirrors enterprise patterns where you serve multiple personas from the same data pipeline. It also showcases my understanding of Snowflake's native app ecosystem, which is a premium feature not all candidates have experience with."

---

## 📚 References

- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Main Project README](../../README.md)

---

## 🎯 Next Steps

1. ✅ Deploy the Streamlit-in-Snowflake dashboard
2. ✅ Take screenshots of the dashboard running in Snowsight
3. ✅ Update main README with dual-dashboard architecture diagram
4. ✅ Document deployment experience in portfolio
5. ✅ Practice explaining the architectural decision in interviews

---

**Built with ❤️ using Snowflake Native Apps**
