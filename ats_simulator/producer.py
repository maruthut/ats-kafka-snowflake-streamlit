"""
ATS (Automatic Train Supervision) Telemetry Simulator
Generates realistic train telemetry data and publishes to Kafka
"""
import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer
import os

# Kafka configuration
conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    'client.id': 'ats-simulator'
}
producer = Producer(conf)

# Constants
EMPTY_TRAIN_WEIGHT_TONS = 135
AVG_PASSENGER_WEIGHT_KG = 65
MAX_PASSENGERS = 764
MAX_PASSENGER_LOAD = 600  # Threshold for overcrowding alert
MAX_POWER_DRAW_KW = 150

def simulate_passenger_count():
    """Simulate realistic passenger count based on time of day and weekday"""
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
    """Callback for Kafka producer delivery reports"""
    if err is not None:
        print(f'❌ Message delivery failed: {err}')
    else:
        print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}]')

def run_simulator():
    """Main simulator loop"""
    print("🚆 Starting ATS Telemetry Simulator...")
    print(f"📡 Publishing to Kafka at {conf['bootstrap.servers']}")
    print(f"⏰ Publishing interval: 30 seconds\n")
    
    while True:
        try:
            data = generate_telemetry()
            
            # Publish to Kafka
            producer.produce(
                'ats_telemetry',
                value=json.dumps(data),
                callback=delivery_report
            )
            producer.flush()
            
            print(f"📊 Published: Train {data['train_id']} | "
                  f"Passengers: {data['passenger_count']} | "
                  f"Power: {data['power_draw_kw']}kW | "
                  f"Alerts: {data['alerts']}")
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_simulator()
