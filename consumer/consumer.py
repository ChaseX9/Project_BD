import json
import subprocess
from kafka import KafkaConsumer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Basic config coming from env vars
USER_ID = os.getenv("USER_ID")        # used mainly for logs / filenames
TOPIC = os.getenv("TOPIC")            # Kafka topic to consume
GROUP_ID = os.getenv("GROUP_ID")      # consumer group id
BROKER = os.getenv("KAFKA_BROKER")    # Kafka broker address
HDFS_DIR = os.getenv("HDFS_DIR")      # target HDFS directory

# Kafka consumer setup
# Messages are expected to be JSON encoded
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[BROKER],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",  # start from beginning if no offset found
    group_id=GROUP_ID
)

print(f"[{USER_ID}] Consumer started on topic: {TOPIC}")

# Main consume loop
for msg in consumer:
    data = msg.value
    # Simple log to see what's coming in
    print(f"[{USER_ID}] Received:", data)

    # Save message locally first (temporary file)
    # Offset is used to avoid overwriting files
    local_file = f"/tmp/{USER_ID}_msg_{msg.offset}.json"
    with open(local_file, "w") as f:
        f.write(json.dumps(data))

    # Try to push the file to HDFS
    # If HDFS is not available, we just keep the local file
    try:
        subprocess.run(
            ["hdfs", "dfs", "-put", local_file, HDFS_DIR],
            check=False  # don't crash if hdfs command fails
        )
    except FileNotFoundError:
        # Happens for example when running locally without HDFS
        print("[INFO] HDFS not available in this environment. File saved locally only.")
