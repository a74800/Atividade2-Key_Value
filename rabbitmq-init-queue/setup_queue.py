# services/rabbitmq-init-queue/setup_queue.py
import requests
import time
import sys

RABBITMQ_API = "http://haproxy-rabbitmq:15672/api"
USERNAME = "guest"
PASSWORD = "guest"
QUEUE_NAME = "store-events"
EXPECTED_NODES = 3
RETRIES = 30
DELAY = 5


def wait_for_cluster():
    print("[INIT] A aguardar formação completa do cluster RabbitMQ...")

    for i in range(RETRIES):
        try:
            r = requests.get(f"{RABBITMQ_API}/nodes", auth=(USERNAME, PASSWORD))
            if r.status_code == 200:
                nodes = r.json()
                node_count = len(nodes)
                print(f"[INIT] Tentativa {i+1}: {node_count} nós detectados")
                if node_count >= EXPECTED_NODES:
                    print("[INIT] Cluster com número esperado de nós detectado.")
                    return
            else:
                print(f"[INIT] Tentativa {i+1}: Erro ao consultar nodes: {r.status_code}")
        except Exception as e:
            print(f"[INIT] Tentativa {i+1}: Erro de ligação: {e}")
        time.sleep(DELAY)

    print("[INIT] Falha ao detectar cluster após várias tentativas.")
    sys.exit(1)


def create_quorum_queue():
    print(f"[INIT] Criando/verificando fila '{QUEUE_NAME}'...")

    url = f"{RABBITMQ_API}/queues/%2F/{QUEUE_NAME}"  # %2F = /
    data = {
        "durable": True,
        "arguments": {
            "x-queue-type": "quorum",
            "x-quorum-initial-group-size": 3,
            "x-quorum-group-size": 3
        }
    }

    headers = {"Content-Type": "application/json"}

    r = requests.put(url, json=data, auth=(USERNAME, PASSWORD), headers=headers)
    if r.status_code in (201, 204):
        print(f"[INIT] Fila '{QUEUE_NAME}' criada ou já existente.")
    else:
        print(f"[INIT] Erro ao criar fila: {r.status_code} - {r.text}")
        sys.exit(1)


if __name__ == "__main__":
    wait_for_cluster()
    create_quorum_queue()
    print("[INIT] Configuração concluída com sucesso.")
