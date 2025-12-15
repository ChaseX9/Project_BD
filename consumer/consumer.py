import json
import subprocess
from kafka import KafkaConsumer
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des variables nécessaires
# USER_ID sert juste à identifier le consumer dans les logs
USER_ID = os.getenv("USER_ID")
TOPIC = os.getenv("TOPIC")
GROUP_ID = os.getenv("GROUP_ID")
BROKER = os.getenv("KAFKA_BROKER")
HDFS_DIR = os.getenv("HDFS_DIR")

# Création du consumer Kafka
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[BROKER],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),  # conversion des messages en JSON
    auto_offset_reset="earliest",
    group_id=GROUP_ID
)

# Message pour vérifier que le consumer a bien démarré
print(f"[{USER_ID}] Consumer started on topic: {TOPIC}")

# Boucle principale : le consumer écoute en continu
for msg in consumer:
    data = msg.value  # récupération du contenu du message
    print(f"[{USER_ID}] Received:", data)

    # Création d'un fichier temporaire pour stocker le message
    # Le offset est utilisé pour éviter d'écraser les fichiers
    local_file = f"/tmp/{USER_ID}_msg_{msg.offset}.json"
    with open(local_file, "w") as f:
        f.write(json.dumps(data))

    try:
        # Envoi du fichier vers HDFS
        # check=False pour éviter que le programme plante si la commande échoue
        subprocess.run(["hdfs", "dfs", "-put", local_file, HDFS_DIR], check=False)
    except FileNotFoundError:
        # Cas où HDFS n'est pas disponible (par exemple en local)
        print("[INFO] HDFS not available in this environment. File saved locally only.")
