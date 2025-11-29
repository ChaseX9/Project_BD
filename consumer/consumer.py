import json
import subprocess
from kafka import KafkaConsumer
import os
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("USER_ID")
TOPIC = os.getenv("TOPIC")
GROUP_ID = os.getenv("GROUP_ID")
BROKER = os.getenv("KAFKA_BROKER")
HDFS_DIR = os.getenv("HDFS_DIR")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[BROKER],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id=GROUP_ID
)

print(f"[{USER_ID}] Consumer started on topic: {TOPIC}")

for msg in consumer:
    data = msg.value
    print(f"[{USER_ID}] Received:", data)

    local_file = f"/tmp/{USER_ID}_msg_{msg.offset}.json"
    with open(local_file, "w") as f:
        f.write(json.dumps(data))

    try:
        subprocess.run(["hdfs", "dfs", "-put", local_file, HDFS_DIR], check=False)
    except FileNotFoundError:
        print("[INFO] HDFS not available in this environment. File saved locally only.")