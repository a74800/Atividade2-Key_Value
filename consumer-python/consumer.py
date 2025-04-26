import asyncio
import json
import aio_pika
import asyncpg
from redis.asyncio import Redis

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"
QUEUE_NAME = "store-events"

DB_CONFIG = {
    "user": "myuser",
    "password": "mypass",
    "database": "mydatabase",
    "host": "postgres",
    "port": 5432,
}

REDIS_CONFIG = {
    "host": "redis",
    "port": 6379,
    "decode_responses": True
}


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        key = data.get("key")
        value = data.get("value")
        print(f"[✉] Mensagem recebida: {key} → {value}")

        try:
            conn = await asyncpg.connect(**DB_CONFIG)
            await conn.execute("""
                INSERT INTO chave_valor (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, key, value)
            await conn.close()
            print(f"[✔] Gravado no PostgreSQL: {key}")

            redis = Redis(**REDIS_CONFIG)
            await redis.set(key, value)
            print(f"[🧠] Atualizado na cache Redis: {key}")

        except Exception as e:
            print(f"[⚠️] Erro ao gravar na DB. Reenviando mensagem para a fila. Erro: {e}")
            await message.nack(requeue=True)

async def wait_for_rabbitmq():
    while True:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            print("✅ Conectado ao RabbitMQ")
            return connection
        except Exception as e:
            print(f"⏳ A aguardar RabbitMQ... {e}")
            await asyncio.sleep(2)


async def main():
    # Aguardar RabbitMQ estar disponível
    connection = await wait_for_rabbitmq()
    # Conectar ao Redis
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    print("[*] A aguardar mensagens... (CTRL+C para sair)")
    await queue.consume(process_message)

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
