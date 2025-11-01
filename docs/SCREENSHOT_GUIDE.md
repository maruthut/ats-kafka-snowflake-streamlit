# 📸 Screenshot Capture Guide

This guide helps you capture and save dashboard screenshots for your GitHub portfolio.

## 🎯 Quick Instructions

### Windows (Using Snipping Tool or Snip & Sketch)

1. **Open Dashboard**
   ```powershell
   # Ensure dashboard is running
   docker-compose ps streamlit-dashboard
   # Open browser to http://localhost:8501
   ```

2. **Capture Screenshots**
   - Press `Win + Shift + S` to open Snipping Tool
   - Select rectangular area to capture
   - After capture, click notification to open image
   - Save to `docs/images/` directory

3. **Required Screenshots** (in order of appearance):

   **Scroll to top of dashboard:**
   - `dashboard-header.png` - Header with title and controls
   - `kpi-metrics.png` - Four KPI boxes (Active Trains, Avg Passengers, Active Alerts, Avg Power Draw)
   
   **Active Alerts section:**
   - `active-alerts.png` - Alert boxes showing HIGH_POWER_DRAW warnings
   
   **Real-Time Metrics section:**
   - `passenger-timeline.png` - Left chart (Passenger Count by Train)
   - `power-timeline.png` - Right chart (Power Consumption by Train)
   
   **Distribution section:**
   - `passenger-distribution.png` - Left chart (histogram)
   - `speed-distribution.png` - Right chart (box plot)
   
   **Hourly Statistics section:**
   - `readings-per-hour.png` - Left chart (bar chart)
   - `incidents-per-hour.png` - Right chart (line chart with Overcrowding/High Power)
   
   **Train Status section:**
   - `train-status-table.png` - Data table at bottom

### Alternative: Browser DevTools (Full Page Screenshot)

#### Chrome/Edge:
```
1. Press F12 to open DevTools
2. Press Ctrl+Shift+P to open Command Palette
3. Type "screenshot" and select "Capture full size screenshot"
4. Image saves to Downloads folder
5. Crop sections and save to docs/images/
```

#### Firefox:
```
1. Press Shift+F2 to open Developer Toolbar
2. Type "screenshot --fullpage" and press Enter
3. Image saves to Downloads folder
4. Crop sections and save to docs/images/
```

## 📁 File Organization

Create these files in `docs/images/`:

```
docs/
└── images/
    ├── dashboard-header.png        (1920x200px recommended)
    ├── kpi-metrics.png             (1920x300px recommended)
    ├── active-alerts.png           (1920x400px recommended)
    ├── passenger-timeline.png      (960x400px recommended)
    ├── power-timeline.png          (960x400px recommended)
    ├── passenger-distribution.png  (960x350px recommended)
    ├── speed-distribution.png      (960x350px recommended)
    ├── readings-per-hour.png       (960x350px recommended)
    ├── incidents-per-hour.png      (960x350px recommended)
    └── train-status-table.png      (1920x400px recommended)
```

## 🖼️ Image Quality Tips

1. **Resolution:** Capture at 100% browser zoom for crisp images
2. **Format:** PNG format preserves chart quality better than JPG
3. **Size:** Keep individual images under 1MB for fast GitHub loading
4. **Cropping:** Include relevant UI but remove excess whitespace
5. **Consistency:** Use same browser zoom level for all captures

## 🎨 Optional: Annotate Screenshots

Use tools like:
- **Windows:** Paint, Paint 3D, Snip & Sketch
- **Online:** Figma, Canva (free accounts)
- **Professional:** Photoshop, GIMP

Add annotations like:
- Arrows pointing to key features
- Text boxes explaining metrics
- Highlight boxes around important data

## ✅ Verification Checklist

Before committing:

- [ ] All 10 images saved to `docs/images/`
- [ ] Images are PNG format
- [ ] Filenames match exactly (lowercase, hyphens)
- [ ] Images are clear and readable
- [ ] No sensitive data visible (if any)
- [ ] File sizes reasonable (<1MB each)

## 🚀 Commit Screenshots to GitHub

```powershell
# Navigate to project root
cd C:\Maruthu\Projects\ats_snowflake_snowlit

# Check what will be added
git status

# Add all images
git add docs/images/*.png

# Commit with descriptive message
git commit -m "Add live dashboard screenshots for portfolio showcase"

# Push to GitHub
git push origin main
```

## 🌐 View on GitHub

After pushing, your screenshots will be visible at:

- **Main README:** https://github.com/maruthut/ats-kafka-snowflake-streamlit
- **Screenshot Guide:** https://github.com/maruthut/ats-kafka-snowflake-streamlit/blob/main/docs/DASHBOARD_SCREENSHOTS.md
- **Raw Images:** https://github.com/maruthut/ats-kafka-snowflake-streamlit/tree/main/docs/images

## 💡 Pro Tips for Portfolio

1. **Update LinkedIn:**
   - Add screenshots to project description
   - Link to GitHub repository
   - Mention technologies used

2. **Resume Enhancement:**
   - "Built real-time data pipeline with 115+ concurrent streams"
   - "Implemented Kafka-Snowflake ELT with sub-minute latency"
   - "Created interactive dashboard with Streamlit and Plotly"

3. **Interview Talking Points:**
   - Explain architecture decisions (ELT vs ETL)
   - Discuss troubleshooting challenges (password escaping)
   - Showcase monitoring capabilities (alerts, metrics)
   - Highlight production-ready features (health checks, error handling)

## 🎓 Portfolio Presentation

When showing this project:

1. **Start with architecture diagram** (in README)
2. **Show live dashboard** (http://localhost:8501)
3. **Demonstrate data flow:**
   - ATS simulator logs
   - Kafka messages
   - Snowflake data
   - Dashboard refresh
4. **Explain technical decisions:**
   - Why ELT over ETL?
   - Why Dynamic Tables?
   - Why RSA keys for Kafka Connect?
5. **Discuss challenges overcome:**
   - Docker Compose password escaping
   - Snowflake connector authentication
   - Performance optimization

---

**📌 Remember:** These screenshots prove you built a working, production-quality system, not just theoretical knowledge!
