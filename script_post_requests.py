# script_put_requests.py

import requests
import time

URL = "http://localhost:8080/store"  # O endpoint correto

for i in range(20):
    data = {
        "key": f"chave_{i}",
        "value": f"valor_{i}"
    }
    try:
        response = requests.put(URL, json=data)
        print(f"Pedido {i}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro no pedido {i}: {e}")
    time.sleep(0.2)  # Pequena pausa de 200ms entre pedidos
