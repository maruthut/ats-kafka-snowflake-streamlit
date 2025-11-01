#!/usr/bin/env python3
"""
ATS Pipeline Testing Script
Verifies the entire ATS pipeline is working correctly
"""
import subprocess
import sys
import time
from pathlib import Path
import json

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def add_pass(self):
        self.total += 1
        self.passed += 1
    
    def add_fail(self):
        self.total += 1
        self.failed += 1
    
    def pass_rate(self):
        if self.total == 0:
            return 0
        return round((self.passed / self.total) * 100, 1)

def print_color(message, color, newline=True):
    """Print colored message"""
    end = '\n' if newline else ''
    print(f"{color}{message}{Colors.RESET}", end=end)

def run_command(command, check=True, timeout=10):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None

def test_component(name, test_func, success_msg, failure_msg):
    """Test a component and print result"""
    print_color(f"Testing: {name}...", Colors.YELLOW, newline=False)
    
    try:
        result = test_func()
        if result:
            print_color(" ✅ PASS", Colors.GREEN)
            print_color(f"  → {success_msg}", Colors.GRAY)
            return True
        else:
            print_color(" ❌ FAIL", Colors.RED)
            print_color(f"  → {failure_msg}", Colors.GRAY)
            return False
    except Exception as e:
        print_color(" ❌ ERROR", Colors.RED)
        print_color(f"  → {str(e)}", Colors.GRAY)
        return False

def test_docker():
    """Test if Docker is running"""
    result = run_command("docker info", check=False)
    return result is not None

def test_env_file():
    """Test if .env file exists"""
    return Path(".env").exists()

def test_docker_service(service_name):
    """Test if a Docker service is running"""
    result = run_command(f"docker-compose ps -q {service_name}", check=False)
    return result is not None and len(result) > 0

def test_http_endpoint(url, timeout=5):
    """Test if HTTP endpoint is accessible"""
    try:
        import urllib.request
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except:
        return False

def test_kafka_topic():
    """Test if Kafka topic exists"""
    result = run_command(
        "docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list",
        check=False,
        timeout=10
    )
    return result and "ats_telemetry" in result

def test_kafka_messages():
    """Test if messages exist in Kafka"""
    result = run_command(
        "docker exec kafka kafka-console-consumer "
        "--bootstrap-server localhost:9092 "
        "--topic ats_telemetry "
        "--from-beginning "
        "--max-messages 1 "
        "--timeout-ms 5000",
        check=False,
        timeout=10
    )
    return result is not None and len(result) > 0

def test_snowflake_connector():
    """Test if Snowflake connector is running"""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8083/connectors/snowflake-sink-connector/status")
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        return data.get("connector", {}).get("state") == "RUNNING"
    except:
        return False

def print_header(title):
    """Print section header"""
    print()
    print_color(title, Colors.CYAN)
    print_color("-" * 80, Colors.GRAY)

def print_summary(results):
    """Print test summary"""
    print()
    print()
    print_color("📊 Test Summary", Colors.CYAN)
    print_color("=" * 80, Colors.CYAN)
    print()
    print(f"  Total Tests: {results.total}")
    print_color(f"  Passed:      {results.passed}", Colors.GREEN)
    print_color(f"  Failed:      {results.failed}", Colors.RED)
    print()
    
    pass_rate = results.pass_rate()
    print("  Pass Rate:   ", end='')
    
    if pass_rate >= 90:
        print_color(f"{pass_rate}% 🎉", Colors.GREEN)
    elif pass_rate >= 70:
        print_color(f"{pass_rate}% ⚠️", Colors.YELLOW)
    else:
        print_color(f"{pass_rate}% ❌", Colors.RED)
    
    print()
    print_color("=" * 80, Colors.CYAN)
    print()

def print_troubleshooting():
    """Print troubleshooting steps"""
    print_color("🔧 Troubleshooting Steps:", Colors.YELLOW)
    print()
    
    if not Path(".env").exists():
        print_color("  1. Create .env file: cp .env.example .env", Colors.WHITE)
    
    print_color("  2. Check Docker logs: docker-compose logs -f", Colors.WHITE)
    print_color("  3. Verify Snowflake credentials in .env", Colors.WHITE)
    print_color("  4. Register connector: python kafka_connect/register_connector.py", Colors.WHITE)
    print_color("  5. Restart services: docker-compose restart", Colors.WHITE)
    print()

def print_success_info():
    """Print success information"""
    print_color("✅ All tests passed! Your pipeline is working correctly!", Colors.GREEN)
    print()
    print_color("🌐 Access Points:", Colors.CYAN)
    print_color("  • Dashboard:      http://localhost:8501", Colors.WHITE)
    print_color("  • Kafka Connect:  http://localhost:8083", Colors.WHITE)
    print()
    print_color("📝 Next Steps:", Colors.CYAN)
    print_color("  1. Open dashboard in browser", Colors.WHITE)
    print_color("  2. Verify data is appearing in Snowflake", Colors.WHITE)
    print_color("  3. Check alerts are triggering", Colors.WHITE)
    print_color("  4. Let it run for a few minutes to see trends", Colors.WHITE)
    print()

def print_additional_commands():
    """Print additional useful commands"""
    print_color("📚 Additional Commands:", Colors.CYAN)
    print_color("  • View logs:        docker-compose logs -f [service-name]", Colors.GRAY)
    print_color("  • Restart service:  docker-compose restart [service-name]", Colors.GRAY)
    print_color("  • Stop all:         docker-compose stop", Colors.GRAY)
    print_color("  • Check status:     docker-compose ps", Colors.GRAY)
    print()

def main():
    """Main function"""
    print_color("🧪 ATS Pipeline Testing Script", Colors.CYAN)
    print_color("=" * 80, Colors.CYAN)
    print()
    
    results = TestResults()
    
    # Pre-Flight Checks
    print_header("📋 Pre-Flight Checks")
    
    if test_component("Docker Desktop", test_docker,
                      "Docker is running",
                      "Docker Desktop is not running. Please start it."):
        results.add_pass()
    else:
        results.add_fail()
    
    print()
    
    if test_component(".env Configuration", test_env_file,
                      ".env file found",
                      ".env file missing. Copy .env.example to .env"):
        results.add_pass()
    else:
        results.add_fail()
    
    # Docker Services Health
    print_header("🐳 Docker Services Health")
    
    services = [
        ("Zookeeper", "zookeeper", "Zookeeper container is up", "Zookeeper is not running"),
        ("Kafka Broker", "kafka", "Kafka broker is up", "Kafka is not running"),
        ("ATS Simulator", "ats-simulator", "ATS simulator is running", "ATS simulator is not running"),
    ]
    
    for name, service, success, failure in services:
        if test_component(name, lambda s=service: test_docker_service(s), success, failure):
            results.add_pass()
        else:
            results.add_fail()
    
    # Test Kafka Connect HTTP endpoint
    if test_component("Kafka Connect", lambda: test_http_endpoint("http://localhost:8083/"),
                      "Kafka Connect REST API is responding",
                      "Kafka Connect is not accessible"):
        results.add_pass()
    else:
        results.add_fail()
    
    # Test Streamlit Dashboard
    if test_component("Streamlit Dashboard", lambda: test_http_endpoint("http://localhost:8501/_stcore/health"),
                      "Dashboard is accessible at http://localhost:8501",
                      "Dashboard is not accessible"):
        results.add_pass()
    else:
        results.add_fail()
    
    # Data Flow Verification
    print_header("📡 Data Flow Verification")
    
    if test_component("Kafka Topic (ats_telemetry)", test_kafka_topic,
                      "Topic 'ats_telemetry' exists",
                      "Topic not found. May need time to auto-create."):
        results.add_pass()
    else:
        results.add_fail()
    
    if test_component("Kafka Messages", test_kafka_messages,
                      "Messages are being produced to Kafka",
                      "No messages found. Check ATS simulator logs."):
        results.add_pass()
    else:
        results.add_fail()
    
    if test_component("Snowflake Connector", test_snowflake_connector,
                      "Snowflake connector is RUNNING",
                      "Connector not running. Run register_connector.py"):
        results.add_pass()
    else:
        results.add_fail()
    
    # Print Summary
    print_summary(results)
    
    # Print recommendations
    if results.failed > 0:
        print_troubleshooting()
    else:
        print_success_info()
    
    print_additional_commands()

if __name__ == "__main__":
    main()
