import json
import time
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# Retrieve configuration values from environment variables
USER_ID = os.getenv("USER_ID")
TOPIC = os.getenv("TOPIC")
BROKER = os.getenv("KAFKA_BROKER")

# Create a Kafka producer instance
# Messages are serialized into JSON before being sent
producer = KafkaProducer(
    bootstrap_servers=[BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print(f"[{USER_ID}] Producer started on topic: {TOPIC}")

# Infinite loop to simulate a real-time IoT data stream
while True:
    # Create a simulated IoT sensor message
    message = {
        "producer": USER_ID,
        "sensor_id": 1,
        "temperature": round(20 + (time.time() % 5), 2),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    # Send the message to the Kafka topic
    producer.send(TOPIC, message)
    print(f"[{USER_ID}] Sent:", message)
    
    # Wait 5 seconds before sending the next message

    time.sleep(5)
