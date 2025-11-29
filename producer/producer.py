import json
import time
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("USER_ID")
TOPIC = os.getenv("TOPIC")
BROKER = os.getenv("KAFKA_BROKER")

producer = KafkaProducer(
    bootstrap_servers=[BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print(f"[{USER_ID}] Producer started on topic: {TOPIC}")

while True:
    message = {
        "producer": USER_ID,
        "sensor_id": 1,
        "temperature": round(20 + (time.time() % 5), 2),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    producer.send(TOPIC, message)
    print(f"[{USER_ID}] Sent:", message)
    time.sleep(5)
