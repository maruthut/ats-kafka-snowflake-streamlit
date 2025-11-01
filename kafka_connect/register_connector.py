#!/usr/bin/env python3
"""
Snowflake Kafka Connector Registration Script
Registers the Snowflake sink connector with Kafka Connect
"""
import json
import time
import sys
import os
import urllib.request
import urllib.error
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load .env file from project root"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(message, color):
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")

def load_connector_config():
    """
    Load connector configuration from JSON file and substitute environment variables.
    
    Returns:
        dict: Connector configuration with env vars substituted
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'snowflake_connector_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Substitute environment variables
        config_str = json.dumps(config)
        for key, value in os.environ.items():
            if key.startswith('SNOWFLAKE_'):
                config_str = config_str.replace(f'${{{key}}}', value)
        
        config = json.loads(config_str)
        
        # Validate required fields
        required_fields = ['snowflake.url.name', 'snowflake.user.name', 'snowflake.database.name']
        for field in required_fields:
            if f'${{{field}' in json.dumps(config):
                print_color(f"❌ Error: Environment variable not set for {field}", Colors.RED)
                sys.exit(1)
        
        return config
        
    except FileNotFoundError:
        print_color("❌ Error: snowflake_connector_config.json not found", Colors.RED)
        print_color("Expected location: kafka_connect/snowflake_connector_config.json", Colors.YELLOW)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_color(f"❌ Error: Invalid JSON in config file: {e}", Colors.RED)
        sys.exit(1)

def wait_for_kafka_connect(max_retries=30):
    """Wait for Kafka Connect to be ready"""
    print_color("Waiting for Kafka Connect to be ready...", Colors.YELLOW)
    
    for i in range(max_retries):
        try:
            req = urllib.request.Request("http://localhost:8083/")
            urllib.request.urlopen(req, timeout=5)
            print_color("✅ Kafka Connect is ready!", Colors.GREEN)
            return True
        except Exception:
            print(f"  Attempt {i+1}/{max_retries}...", end='\r')
            time.sleep(2)
    
    print_color("\n❌ Kafka Connect is not responding after 60 seconds", Colors.RED)
    return False

def register_connector(config):
    """Register the Snowflake connector"""
    print_color("\n🔧 Registering Snowflake Sink Connector...", Colors.CYAN)
    
    try:
        # Prepare request
        url = "http://localhost:8083/connectors"
        data = json.dumps(config).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Send request
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        
        print_color("✅ Connector registered successfully!", Colors.GREEN)
        print(json.dumps(result, indent=2))
        return True
        
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print_color("⚠️  Connector already exists. Updating...", Colors.YELLOW)
            return update_connector(config)
        else:
            print_color(f"❌ HTTP Error: {e.code} - {e.reason}", Colors.RED)
            print(e.read().decode())
            return False
    except Exception as e:
        print_color(f"❌ Error registering connector: {e}", Colors.RED)
        return False

def update_connector(config):
    """Update existing connector configuration"""
    try:
        connector_name = config['name']
        url = f"http://localhost:8083/connectors/{connector_name}/config"
        data = json.dumps(config['config']).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        
        print_color("✅ Connector updated successfully!", Colors.GREEN)
        print(json.dumps(result, indent=2))
        return True
        
    except Exception as e:
        print_color(f"❌ Error updating connector: {e}", Colors.RED)
        return False

def check_connector_status(connector_name):
    """Check the status of the connector"""
    print_color("\n📊 Checking connector status...", Colors.CYAN)
    
    try:
        url = f"http://localhost:8083/connectors/{connector_name}/status"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=10)
        status = json.loads(response.read().decode())
        
        print(json.dumps(status, indent=2))
        
        # Check if connector is running
        connector_state = status.get('connector', {}).get('state')
        if connector_state == 'RUNNING':
            print_color("\n✅ Connector is RUNNING!", Colors.GREEN)
        else:
            print_color(f"\n⚠️  Connector state: {connector_state}", Colors.YELLOW)
        
        return True
        
    except Exception as e:
        print_color(f"❌ Error checking status: {e}", Colors.RED)
        return False

def main():
    """Main function"""
    print_color("=" * 80, Colors.CYAN)
    print_color("🚀 Snowflake Kafka Connector Registration", Colors.CYAN)
    print_color("=" * 80, Colors.CYAN)
    print()
    
    # Wait for Kafka Connect
    if not wait_for_kafka_connect():
        print_color("\n💡 Tips:", Colors.YELLOW)
        print("  1. Make sure Docker containers are running: docker-compose ps")
        print("  2. Check Kafka Connect logs: docker-compose logs kafka-connect")
        print("  3. Wait a bit longer and try again")
        sys.exit(1)
    
    # Load configuration
    config = load_connector_config()
    
    # Register connector
    if not register_connector(config):
        print_color("\n💡 If this persists:", Colors.YELLOW)
        print("  1. Check your .env file has correct Snowflake credentials")
        print("  2. Verify Snowflake user has RSA public key assigned")
        print("  3. Check connector logs: docker-compose logs kafka-connect")
        sys.exit(1)
    
    # Check status
    time.sleep(2)
    check_connector_status(config['name'])
    
    print()
    print_color("=" * 80, Colors.CYAN)
    print_color("✨ Connector registration complete!", Colors.GREEN)
    print_color("=" * 80, Colors.CYAN)
    print()
    print_color("📝 Next steps:", Colors.CYAN)
    print("  1. Verify data is flowing: docker-compose logs ats-simulator")
    print("  2. Check Snowflake: SELECT COUNT(*) FROM ATS_RAW_JSON;")
    print("  3. Open dashboard: http://localhost:8501")
    print()

if __name__ == "__main__":
    main()
