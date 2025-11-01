# 📚 Project Documentation

This directory contains comprehensive documentation for the ATS Kafka-Snowflake-Streamlit pipeline project.

## 📄 Available Documents

### 🖼️ [DASHBOARD_SCREENSHOTS.md](DASHBOARD_SCREENSHOTS.md)
Complete visual documentation of the live dashboard with detailed explanations of each feature:
- Key Performance Indicators
- Active Alerts System
- Real-Time Metrics (Passenger & Power timelines)
- Distribution Analytics
- Hourly Statistics
- Train Status Overview

### 📸 [SCREENSHOT_GUIDE.md](SCREENSHOT_GUIDE.md)
Step-by-step instructions for capturing and saving dashboard screenshots:
- How to capture screenshots on Windows
- Recommended image sizes and formats
- File naming conventions
- Git commit instructions
- Portfolio presentation tips

### 📁 images/
Directory for storing dashboard screenshots:
```
images/
├── dashboard-header.png
├── kpi-metrics.png
├── active-alerts.png
├── passenger-timeline.png
├── power-timeline.png
├── passenger-distribution.png
├── speed-distribution.png
├── readings-per-hour.png
├── incidents-per-hour.png
└── train-status-table.png
```

## 🎯 Quick Actions

### View Live Dashboard
```bash
# Ensure containers are running
docker-compose ps

# Open browser to http://localhost:8501
```

### Capture Screenshots
Follow instructions in [`SCREENSHOT_GUIDE.md`](SCREENSHOT_GUIDE.md)

### Update Documentation
After capturing screenshots, they will automatically appear in [`DASHBOARD_SCREENSHOTS.md`](DASHBOARD_SCREENSHOTS.md) when viewed on GitHub.

---

**Return to:** [Main README](../README.md) | [Troubleshooting Guide](../TROUBLESHOOTING.md) | [Architectural Review](../ARCHITECTURAL_REVIEW.md)
