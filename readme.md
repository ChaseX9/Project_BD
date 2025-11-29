# Real-Time IoT Data Pipeline with Kafka & HDFS  
*A complete end-to-end Big Data ingestion pipeline using Docker, Kafka, Python, and HDFS (Adaltas Cluster)*

---

## 1. Project Summary

This project implements a real-time Big Data ingestion pipeline composed of:

- A **Python Kafka Producer** simulating IoT temperature sensor data  
- A **Kafka cluster** running inside Docker  
- A **Python Kafka Consumer** writing messages as JSON files  
- An upload of those files to the **Adaltas Hadoop cluster**  
- Final storage of the data in **HDFS**

The Kafka topic used in this project is:

```
iot_mael
```

This project demonstrates how streaming data moves from generation → transport → processing → distributed storage.

---

## 2. Why Kafka?

Kafka was selected because:

- It is simple to demonstrate with a producer/consumer model  
- It integrates naturally with Big Data ecosystems (Hadoop, Spark, Hive, etc.)  
- It is widely used in companies for IoT, streaming, and log pipelines  
- It is easy to deploy locally using Docker  
- It provides clear logs that show message movement in real time  


---

## 3. Architecture Overview

```
                ┌──────────────────┐
                │     Producer      │
                │     (Python)      │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │       Kafka       │
                │      (Docker)     │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │     Consumer      │
                │      (Python)     │
                └─────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │       HDFS        │
                │     (Adaltas)     │
                └──────────────────┘


1. Producer generates IoT messages every 5 seconds  
2. Kafka stores and streams messages  
3. Consumer receives data and writes JSON files into `/tmp`  
4. Files are copied locally  
5. Files are uploaded to the Adaltas cluster  
6. Files are imported into HDFS  
```

---

## 4. Installation & Execution Steps


### 4.1 Create `.env`

```
USER_ID=mael
TOPIC=iot_mael
GROUP_ID=iot_group_mael
KAFKA_BROKER=kafka:9092
HDFS_DIR=/user/m.vaudin-ece/kafka_iot/
```

---

### 4.2 Start Docker Environment

```
docker compose up -d
docker ps
```

---

### 4.3 Create Kafka Topic

```
docker exec -it kafka bash
kafka-topics --create --topic iot_mael --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
kafka-topics --list --bootstrap-server localhost:9092
```

---

### 4.4 Run Producer

```
docker exec -it kafka-producer-mael bash
python3 producer.py
```

---

### 4.5 Run Consumer

```
docker exec -it kafka-consumer-mael bash
python3 consumer.py
```

---

### 4.6 Retrieve Generated JSON Files

```
docker cp kafka-consumer-mael:/tmp/. ./data/
```

---

### 4.7 Upload JSON Files to Adaltas

```
scp data/*.json m.vaudin-ece@edge-1.au.adaltas.cloud:/home/m.vaudin-ece/
```

---

### 4.8 Import JSON Files Into HDFS

```
ssh m.vaudin-ece@edge-1.au.adaltas.cloud
hdfs dfs -mkdir -p /user/m.vaudin-ece/kafka_iot/
hdfs dfs -put *.json /user/m.vaudin-ece/kafka_iot/
hdfs dfs -ls /user/m.vaudin-ece/kafka_iot/
hdfs dfs -cat /user/m.vaudin-ece/kafka_iot/*.json
```

---

## 5. Minimal Working Example

### Producer Example
```python
msg = {
  "producer": USER_ID,
  "timestamp": datetime.utcnow().isoformat(),
  "sensor_id": 1,
  "temperature": 20 + (time.time() % 5)
}
```

### Consumer Example
```python
filename = f"/tmp/{USER_ID}_msg_{counter}.json"
with open(filename, "w") as f:
    json.dump(data, f, indent=2)
```

---

## 6. How This Fits a Big Data Ecosystem

This project demonstrates the ingestion component of a standard Big Data architecture:

- Kafka → ingestion  
- Consumer → preprocessing  
- HDFS → distributed storage  
 
---

## 7. Challenges Encountered & Solutions

### 7.1 Kafka Metadata Timeout
```
KafkaTimeoutError: Failed to update metadata
```
**Cause:** wrong advertised listeners  
**Fix:** use internal hostname

```
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
```

---

### 7.2 HDFS Command Not Available in Docker
```
FileNotFoundError: 'hdfs'
```
**Cause:** Docker does not include Hadoop tools  
**Fix:** HDFS upload done manually from the host.

---

## 8. Our Setup Notes (What We Learned)

- We learned the difference between Docker internal hostnames (`kafka:9092`) and localhost.  
- Kafka requires Zookeeper to be ready before starting.  
- Docker containers cannot run HDFS commands.  
- We became more comfortable using SCP and HDFS commands.  
- `.env` formatting errors can crash an entire environment.

---

## 9. Repository Structure

```
Project_BD/
 ├─ docker-compose.yml
 ├─ .env
 ├─ readme.md
 ├─ producer/
 │    ├─ producer.py
 │    ├─ requirements.txt
 ├─ consumer/
 │    ├─ consumer.py
 │    ├─ requirements.txt
 ├─ data/
 └─ screenshots/
```

---

## 10. Conclusion

This project provides a complete and functional Big Data ingestion pipeline using Kafka, Python, Docker, and HDFS.  
It replicates real workflows used in IoT data collection, log ingestion, and streaming analytics.

