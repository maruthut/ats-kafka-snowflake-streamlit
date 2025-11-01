# PowerShell script to register Snowflake Kafka Connector
# Run this after all services are up

Write-Host "Waiting for Kafka Connect to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Registering Snowflake Sink Connector..." -ForegroundColor Cyan
$body = Get-Content -Path ".\kafka_connect\snowflake_connector_config.json" -Raw

Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

Write-Host ""
Write-Host "Checking connector status..." -ForegroundColor Cyan
$status = Invoke-RestMethod -Uri "http://localhost:8083/connectors/snowflake-sink-connector/status" -Method Get
$status | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "✅ Connector registration complete!" -ForegroundColor Green
