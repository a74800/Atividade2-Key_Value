import asyncio
import json
import aio_pika
import asyncpg
from redis.asyncio.cluster import RedisCluster, ClusterNode

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"
QUEUE_NAME = "store-events"

DB_CONFIG = {
    "user": "root",
    "password": "",
    "database": "appdb",
    "host": "haproxy",
    "port": 26256,
}

REDIS_NODES = [
    ClusterNode("redis-node-1", 6379),
    ClusterNode("redis-node-2", 6379),
    ClusterNode("redis-node-3", 6379),
]

pool = None
redis = None

async def process_message(message: aio_pika.IncomingMessage):
    global pool, redis
    try:
        data = json.loads(message.body.decode())
        key = data.get("key")
        value = data.get("value")
        print(f"[✉] Mensagem recebida: {key} → {value}")

        # PostgreSQL via pool
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chave_valor (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, key, value)
        print(f"[✔] Gravado no PostgreSQL: {key}")

        # Redis cluster
        await redis.set(key, value)
        print(f"[🧠] Atualizado na cache Redis: {key}")

        await message.ack()

    except Exception as e:
        print(f"[⚠️] Erro ao processar mensagem. Reenviando... Erro: {e}")
        await message.nack(requeue=True)

async def wait_for_rabbitmq():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            print("✅ Conectado ao RabbitMQ")
            return connection
        except Exception as e:
            print(f"⏳ A aguardar RabbitMQ... {e}")
            await asyncio.sleep(2)

async def main():
    global pool, redis

    # Criar pool de PostgreSQL
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
    print("✅ Pool de PostgreSQL criado")

    # Criar cliente Redis
    redis = RedisCluster(startup_nodes=REDIS_NODES, decode_responses=True)
    await redis.initialize()
    print("✅ RedisCluster conectado")

    # Aguardar RabbitMQ
    connection = await wait_for_rabbitmq()
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    print("[*] A aguardar mensagens... (CTRL+C para sair)")
    await queue.consume(process_message)

    await asyncio.Future()  # mantém processo vivo

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Interrompido pelo utilizador")
