#!/usr/bin/env pwsh
# Quick Test Script - Verifies the entire ATS pipeline
# Run this after starting docker-compose to verify everything is working

$ErrorActionPreference = "Continue"

Write-Host "🧪 ATS Pipeline Testing Script" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Function to print test result
function Test-Component {
    param (
        [string]$Name,
        [scriptblock]$Test,
        [string]$SuccessMessage,
        [string]$FailureMessage
    )
    
    Write-Host "Testing: $Name..." -ForegroundColor Yellow -NoNewline
    try {
        $result = & $Test
        if ($result) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            Write-Host "  → $SuccessMessage" -ForegroundColor Gray
            return $true
        } else {
            Write-Host " ❌ FAIL" -ForegroundColor Red
            Write-Host "  → $FailureMessage" -ForegroundColor Gray
            return $false
        }
    } catch {
        Write-Host " ❌ ERROR" -ForegroundColor Red
        Write-Host "  → $($_.Exception.Message)" -ForegroundColor Gray
        return $false
    }
}

# Test Results Tracking
$testResults = @{
    Passed = 0
    Failed = 0
    Total = 0
}

Write-Host "📋 Pre-Flight Checks" -ForegroundColor Cyan
Write-Host "-" * 80 -ForegroundColor Gray

# Test 1: Docker is running
$testResults.Total++
$result = Test-Component -Name "Docker Desktop" -Test {
    $dockerRunning = docker info 2>$null
    return $?
} -SuccessMessage "Docker is running" -FailureMessage "Docker Desktop is not running. Please start it."
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

Write-Host ""

# Test 2: .env file exists
$testResults.Total++
$result = Test-Component -Name ".env Configuration" -Test {
    Test-Path .env
} -SuccessMessage ".env file found" -FailureMessage ".env file missing. Copy .env.example to .env"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

Write-Host ""
Write-Host ""

Write-Host "🐳 Docker Services Health" -ForegroundColor Cyan
Write-Host "-" * 80 -ForegroundColor Gray

# Test 3: Zookeeper
$testResults.Total++
$result = Test-Component -Name "Zookeeper" -Test {
    $status = docker-compose ps -q zookeeper 2>$null
    return $null -ne $status
} -SuccessMessage "Zookeeper container is up" -FailureMessage "Zookeeper is not running"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 4: Kafka
$testResults.Total++
$result = Test-Component -Name "Kafka Broker" -Test {
    $status = docker-compose ps -q kafka 2>$null
    return $null -ne $status
} -SuccessMessage "Kafka broker is up" -FailureMessage "Kafka is not running"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 5: Kafka Connect
$testResults.Total++
$result = Test-Component -Name "Kafka Connect" -Test {
    $response = Invoke-WebRequest -Uri "http://localhost:8083/" -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
    return $response.StatusCode -eq 200
} -SuccessMessage "Kafka Connect REST API is responding" -FailureMessage "Kafka Connect is not accessible"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 6: ATS Simulator
$testResults.Total++
$result = Test-Component -Name "ATS Simulator" -Test {
    $status = docker-compose ps -q ats-simulator 2>$null
    return $null -ne $status
} -SuccessMessage "ATS simulator is running" -FailureMessage "ATS simulator is not running"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 7: Streamlit Dashboard
$testResults.Total++
$result = Test-Component -Name "Streamlit Dashboard" -Test {
    $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
    return $response.StatusCode -eq 200
} -SuccessMessage "Dashboard is accessible at http://localhost:8501" -FailureMessage "Dashboard is not accessible"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

Write-Host ""
Write-Host ""

Write-Host "📡 Data Flow Verification" -ForegroundColor Cyan
Write-Host "-" * 80 -ForegroundColor Gray

# Test 8: Kafka Topic Exists
$testResults.Total++
$result = Test-Component -Name "Kafka Topic (ats_telemetry)" -Test {
    $topics = docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>$null
    return $topics -match "ats_telemetry"
} -SuccessMessage "Topic 'ats_telemetry' exists" -FailureMessage "Topic not found. May need time to auto-create."
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 9: Messages in Kafka
$testResults.Total++
$result = Test-Component -Name "Kafka Messages" -Test {
    $output = docker exec kafka kafka-console-consumer `
        --bootstrap-server localhost:9092 `
        --topic ats_telemetry `
        --from-beginning `
        --max-messages 1 `
        --timeout-ms 5000 2>$null
    return $output.Length -gt 0
} -SuccessMessage "Messages are being produced to Kafka" -FailureMessage "No messages found. Check ATS simulator logs."
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

# Test 10: Snowflake Connector Status
$testResults.Total++
$result = Test-Component -Name "Snowflake Connector" -Test {
    try {
        $connector = Invoke-RestMethod -Uri "http://localhost:8083/connectors/snowflake-sink-connector/status" -Method Get -TimeoutSec 5
        return $connector.connector.state -eq "RUNNING"
    } catch {
        return $false
    }
} -SuccessMessage "Snowflake connector is RUNNING" -FailureMessage "Connector not running. Run register_connector.ps1"
if ($result) { $testResults.Passed++ } else { $testResults.Failed++ }

Write-Host ""
Write-Host ""

Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total Tests: " -NoNewline
Write-Host $testResults.Total -ForegroundColor White
Write-Host "  Passed:      " -NoNewline
Write-Host $testResults.Passed -ForegroundColor Green
Write-Host "  Failed:      " -NoNewline
Write-Host $testResults.Failed -ForegroundColor Red
Write-Host ""

$passRate = [math]::Round(($testResults.Passed / $testResults.Total) * 100, 1)
Write-Host "  Pass Rate:   " -NoNewline

if ($passRate -ge 90) {
    Write-Host "$passRate% 🎉" -ForegroundColor Green
} elseif ($passRate -ge 70) {
    Write-Host "$passRate% ⚠️" -ForegroundColor Yellow
} else {
    Write-Host "$passRate% ❌" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Recommendations
if ($testResults.Failed -gt 0) {
    Write-Host "🔧 Troubleshooting Steps:" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path .env)) {
        Write-Host "  1. Create .env file: Copy-Item .env.example .env" -ForegroundColor White
    }
    
    Write-Host "  2. Check Docker logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "  3. Verify Snowflake credentials in .env" -ForegroundColor White
    Write-Host "  4. Register connector: .\kafka_connect\register_connector.ps1" -ForegroundColor White
    Write-Host "  5. Restart services: docker-compose restart" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✅ All tests passed! Your pipeline is working correctly!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "  • Dashboard:      http://localhost:8501" -ForegroundColor White
    Write-Host "  • Kafka Connect:  http://localhost:8083" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Open dashboard in browser" -ForegroundColor White
    Write-Host "  2. Verify data is appearing in Snowflake" -ForegroundColor White
    Write-Host "  3. Check alerts are triggering" -ForegroundColor White
    Write-Host "  4. Let it run for a few minutes to see trends" -ForegroundColor White
    Write-Host ""
}

Write-Host "📚 Additional Commands:" -ForegroundColor Cyan
Write-Host "  • View logs:        docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "  • Restart service:  docker-compose restart [service-name]" -ForegroundColor Gray
Write-Host "  • Stop all:         docker-compose stop" -ForegroundColor Gray
Write-Host "  • Check status:     docker-compose ps" -ForegroundColor Gray
Write-Host ""
