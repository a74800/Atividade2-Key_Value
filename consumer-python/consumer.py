import asyncio
import json
import aio_pika
import asyncpg
from redis.asyncio.cluster import RedisCluster, ClusterNode
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://guest:guest@haproxy-rabbitmq:5672/"
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
        op = data.get("op", "put")  # default = put
        key = data.get("key")
        value = data.get("value")

        if op == "put":
            logger.info(f"[PUT] {key} → {value}")

            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO chave_valor (key, value)
                    VALUES ($1, $2)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """, key, value)
            await redis.set(key, value)
            logger.info(f"[✔] Atualizado: DB + Redis [{key}]")

        elif op == "delete":
            logger.info(f"[DELETE] {key}")
            async with pool.acquire() as conn:
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM chave_valor WHERE key = $1)", key
                )

            if not exists:
                logger.info(f"Chave {key} ainda não existe na BD. A reenviar para a queue...")
                await message.nack(requeue=True)
                return

            # Se existir, apagar
            async with pool.acquire() as conn:
                await conn.execute("DELETE FROM chave_valor WHERE key = $1", key)
            await redis.delete(key)
            logger.info(f"Apagado: DB + Redis [{key}]")

        else:
            logger.warning(f"Operação desconhecida: {op}")

        await message.ack()

    except Exception as e:
        logger.error(f" Erro ao processar mensagem: {e}")
        await message.nack(requeue=True)

@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((aio_pika.exceptions.AMQPConnectionError, aio_pika.exceptions.AMQPChannelError)),
    before_sleep=lambda retry_state: logger.info(f"Tentativa {retry_state.attempt_number} de reconexão ao RabbitMQ...")
)
async def connect_to_rabbitmq():
    try:
        connection = await aio_pika.connect_robust(
            RABBITMQ_URL,
            timeout=30,
            client_properties={
                "connection_name": f"consumer-{asyncio.current_task().get_name()}"
            }
        )
        logger.info("Conectado ao RabbitMQ")
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar ao RabbitMQ: {e}")
        raise

async def main():
    global pool, redis

    # Criar pool de PostgreSQL
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
        logger.info("Pool de PostgreSQL criado")
    except Exception as e:
        logger.error(f"Erro ao criar pool PostgreSQL: {e}")
        return

    # Criar cliente Redis
    redis = RedisCluster(startup_nodes=REDIS_NODES, decode_responses=True)
    for i in range(10):
        try:
            await redis.initialize()
            logger.info("RedisCluster conectado")
            break
        except Exception as e:
            logger.error(f"Tentativa {i+1}/10 - A aguardar Redis Cluster... {e}")
            await asyncio.sleep(5)
    else:
        logger.error("Falha ao conectar ao Redis Cluster após 10 tentativas.")
        return

    while True:
        try:
            # Aguardar RabbitMQ
            connection = await connect_to_rabbitmq()
            channel = await connection.channel()
            
            # Conectar à queue existente (não declarar)
            queue = await channel.get_queue("store-events", ensure=False)

            logger.info("A aguardar mensagens... (CTRL+C para sair)")
            await queue.consume(process_message)

            # Manter a conexão viva
            await asyncio.Future()

        except KeyboardInterrupt:
            logger.info("Interrompido pelo utilizador")
            break
        except Exception as e:
            logger.error(f"Erro na conexão RabbitMQ: {e}")
            await asyncio.sleep(5)  # Esperar antes de tentar reconectar
        finally:
            if 'connection' in locals():
                await connection.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(" Interrompido pelo utilizador")
