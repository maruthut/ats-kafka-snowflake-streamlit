"""
ATS (Automatic Train Supervision) Telemetry Simulator
Generates realistic train telemetry data and publishes to Kafka
"""
import json
import time
import random
import signal
import sys
from datetime import datetime
from confluent_kafka import Producer, KafkaException
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka configuration with improved settings
conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    'client.id': 'ats-simulator',
    'acks': 'all',  # Wait for all replicas to acknowledge
    'retries': 3,  # Retry failed sends
    'retry.backoff.ms': 1000,  # Wait 1s between retries
    'max.in.flight.requests.per.connection': 1,  # Ensure ordering
    'compression.type': 'snappy',  # Compress messages
    'linger.ms': 100,  # Batch messages for 100ms
    'batch.size': 16384  # Batch size in bytes
}

# Initialize producer with error handling
try:
    producer = Producer(conf)
    logger.info("Kafka producer initialized successfully")
except KafkaException as e:
    logger.error(f"Failed to initialize Kafka producer: {e}")
    sys.exit(1)

# Constants
EMPTY_TRAIN_WEIGHT_TONS = 135
AVG_PASSENGER_WEIGHT_KG = 65
MAX_PASSENGERS = 764
MAX_PASSENGER_LOAD = 600  # Threshold for overcrowding alert
MAX_POWER_DRAW_KW = 150
PUBLISH_INTERVAL_SECONDS = 30
TRAIN_ID_RANGE = (100, 999)
SPEED_MAX_KMH = 80

# Graceful shutdown flag
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def validate_telemetry(data):
    """Validate telemetry data before sending"""
    required_fields = ['timestamp', 'train_id', 'passenger_count', 'total_weight_tons', 
                       'power_draw_kw', 'speed_kmh', 'location', 'alerts']
    
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate ranges
    if not (0 <= data['passenger_count'] <= MAX_PASSENGERS):
        logger.error(f"Invalid passenger count: {data['passenger_count']}")
        return False
    
    if data['speed_kmh'] < 0 or data['speed_kmh'] > SPEED_MAX_KMH:
        logger.error(f"Invalid speed: {data['speed_kmh']}")
        return False
    
    return True

def simulate_passenger_count():
    """
    Simulate realistic passenger count based on time of day and weekday.
    
    Logic:
    - Weekends: 20-100 passengers (light usage)
    - Peak hours (7-10 AM, 5-8 PM): 200-764 passengers
    - Off-peak: 50-200 passengers
    
    Returns:
        int: Passenger count between 0 and MAX_PASSENGERS
    """
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # Weekend logic
    if weekday >= 5:
        base = random.randint(20, 100)
    # Peak hours (morning and evening rush)
    elif 7 <= hour <= 10 or 17 <= hour <= 20:
        base = random.randint(200, MAX_PASSENGERS)
    # Off-peak hours
    else:
        base = random.randint(50, 200)
    
    return min(base, MAX_PASSENGERS)

def calculate_total_weight(passenger_count):
    """Calculate total train weight including passengers"""
    passenger_weight_tons = (passenger_count * AVG_PASSENGER_WEIGHT_KG) / 1000
    return EMPTY_TRAIN_WEIGHT_TONS + passenger_weight_tons

def estimate_power_draw(weight):
    """Estimate power draw based on total weight"""
    # Base power + weight-dependent component
    power = 80 + (0.5 * weight)
    return round(power, 2)

def generate_telemetry():
    """Generate a single telemetry record"""
    passenger_count = simulate_passenger_count()
    total_weight = calculate_total_weight(passenger_count)
    power_draw = estimate_power_draw(total_weight)
    
    telemetry = {
        "timestamp": datetime.utcnow().isoformat(),
        "train_id": f"A{random.randint(100, 999)}",
        "passenger_count": passenger_count,
        "total_weight_tons": round(total_weight, 2),
        "power_draw_kw": power_draw,
        "speed_kmh": round(random.uniform(0, 80), 2),
        "location": {
            "latitude": round(random.uniform(40.7, 40.9), 6),
            "longitude": round(random.uniform(-74.1, -73.9), 6)
        },
        "alerts": {
            "overcrowding": passenger_count > MAX_PASSENGER_LOAD,
            "high_power_draw": power_draw > MAX_POWER_DRAW_KW
        }
    }
    
    return telemetry

def delivery_report(err, msg):
    """
    Callback for Kafka producer delivery reports.
    
    Args:
        err: Error object if delivery failed
        msg: Message object if delivery succeeded
    """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

def run_simulator():
    """
    Main simulator loop with graceful shutdown and error handling.
    
    Publishes telemetry every PUBLISH_INTERVAL_SECONDS until shutdown signal received.
    """
    logger.info("🚆 Starting ATS Telemetry Simulator...")
    logger.info(f"📡 Publishing to Kafka at {conf['bootstrap.servers']}")
    logger.info(f"⏰ Publishing interval: {PUBLISH_INTERVAL_SECONDS} seconds\n")
    
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    while not shutdown_flag:
        try:
            data = generate_telemetry()
            
            # Validate data before sending
            if not validate_telemetry(data):
                logger.warning("Skipping invalid telemetry data")
                time.sleep(PUBLISH_INTERVAL_SECONDS)
                continue
            
            # Publish to Kafka
            producer.produce(
                'ats_telemetry',
                value=json.dumps(data),
                callback=delivery_report
            )
            
            # Flush with timeout to ensure delivery
            producer.flush(timeout=10)
            
            # Reset failure counter on success
            consecutive_failures = 0
            
            logger.info(f"📊 Published: Train {data['train_id']} | "
                       f"Passengers: {data['passenger_count']} | "
                       f"Power: {data['power_draw_kw']}kW | "
                       f"Alerts: {data['alerts']}")
            
            time.sleep(PUBLISH_INTERVAL_SECONDS)
            
        except KafkaException as e:
            consecutive_failures += 1
            logger.error(f"Kafka error ({consecutive_failures}/{max_consecutive_failures}): {e}")
            
            if consecutive_failures >= max_consecutive_failures:
                logger.critical("Max consecutive failures reached. Shutting down.")
                break
            
            time.sleep(5)
            
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)
    
    # Graceful shutdown
    logger.info("Flushing remaining messages...")
    producer.flush(timeout=30)
    logger.info("🛑 Simulator stopped gracefully")

if __name__ == "__main__":
    run_simulator()
