FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r streamlituser && useradd -r -g streamlituser streamlituser

WORKDIR /app

# Install Python dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

# Copy application code
COPY app.py .

# Create .streamlit directory for config
RUN mkdir -p /app/.streamlit && \
    echo '[server]\nenableCORS = false\nenableXsrfProtection = true\nheadless = true\n' > /app/.streamlit/config.toml

# Change ownership to non-root user
RUN chown -R streamlituser:streamlituser /app

# Switch to non-root user
USER streamlituser

EXPOSE 8501

# Improved health check with retry logic
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
