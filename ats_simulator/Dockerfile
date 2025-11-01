FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r atsuser && useradd -r -g atsuser atsuser

WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

# Copy application code
COPY producer.py .

# Change ownership to non-root user
RUN chown -R atsuser:atsuser /app

# Switch to non-root user
USER atsuser

# Health check - verifies Python process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD pgrep -f "python producer.py" > /dev/null || exit 1

CMD ["python", "-u", "producer.py"]
