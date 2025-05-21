import asyncio
import aiohttp
import random
import string
import logging
import time
import csv
from collections import deque

# ⚙️ Configurações
API_URL = "http://localhost:8070/store"
NUM_PEDIDOS_TOTAIS = 20000  # 100k PUT + 100k GET
NUM_UTILIZADORES = 100
CHAVES_GERADAS = deque()

# 📋 Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
)

# 📊 Métricas
metricas = {
    "put_sucesso": 0,
    "put_erro": 0,
    "get_sucesso": 0,
    "get_erro": 0,
    "put_total_tempo": 0.0,
    "get_total_tempo": 0.0
}

def gerar_chave_valor():
    key = ''.join(random.choices(string.ascii_lowercase, k=10))
    value = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return key, value

async def put_request(session):
    key, value = gerar_chave_valor()
    start = time.time()
    try:
        async with session.put(API_URL, json={"key": key, "value": value}) as response:
            duracao = time.time() - start
            metricas["put_total_tempo"] += duracao
            status = response.status
            if status in [200, 201]:
                metricas["put_sucesso"] += 1
                CHAVES_GERADAS.append(key)
            else:
                metricas["put_erro"] += 1
            logging.info(f"[PUT] {key} → {value} | Status: {status} | Tempo: {duracao:.3f}s")
    except Exception as e:
        metricas["put_erro"] += 1
        logging.error(f"[PUT ERROR] {e}")

async def get_request(session):
    if not CHAVES_GERADAS:
        await asyncio.sleep(0.1)
        return
    key = random.choice(list(CHAVES_GERADAS))
    start = time.time()
    try:
        async with session.get(f"{API_URL}/{key}") as response:
            duracao = time.time() - start
            metricas["get_total_tempo"] += duracao
            status = response.status
            if status == 200:
                metricas["get_sucesso"] += 1
            else:
                metricas["get_erro"] += 1
            result = await response.text()
            logging.info(f"[GET] {key} → {result} | Status: {status} | Tempo: {duracao:.3f}s")
    except Exception as e:
        metricas["get_erro"] += 1
        logging.error(f"[GET ERROR] {e}")

# Simulação aleatória de ações
async def simular_utilizador(session, id, num_pedidos):
    for _ in range(num_pedidos):
        if random.random() < 0.5:
            await put_request(session)
        else:
            await get_request(session)
        await asyncio.sleep(random.uniform(0.01, 0.05))

def escrever_resultados_csv():
    with open("resultados.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Tipo", "Sucesso", "Erro", "Tempo Médio (s)"])
        writer.writerow([
            "PUT",
            metricas["put_sucesso"],
            metricas["put_erro"],
            round(metricas["put_total_tempo"] / max(metricas["put_sucesso"] + metricas["put_erro"], 1), 4)
        ])
        writer.writerow([
            "GET",
            metricas["get_sucesso"],
            metricas["get_erro"],
            round(metricas["get_total_tempo"] / max(metricas["get_sucesso"] + metricas["get_erro"], 1), 4)
        ])
    logging.info("📄 Resultados guardados em resultados.csv")

async def main():
    logging.info(f"🏁 Início do teste: {NUM_UTILIZADORES} utilizadores, {NUM_PEDIDOS_TOTAIS} pedidos no total (PUT + GET).")
    pedidos_por_user = NUM_PEDIDOS_TOTAIS // NUM_UTILIZADORES

    async with aiohttp.ClientSession() as session:
        tarefas = [
            simular_utilizador(session, i, pedidos_por_user)
            for i in range(NUM_UTILIZADORES)
        ]
        await asyncio.gather(*tarefas)

    logging.info("✅ Teste completo.")
    escrever_resultados_csv()

if __name__ == "__main__":
    asyncio.run(main())
