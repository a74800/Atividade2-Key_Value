import asyncio
import aio_pika
import logging
import socket
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do RabbitMQ
RABBITMQ_HOST = "haproxy-rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
RABBITMQ_VHOST = "/"
QUEUE_NAME = "store-events"

# Construir URL do RabbitMQ
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"

async def wait_for_rabbitmq():
    """Espera até que o RabbitMQ esteja pronto para aceitar conexões."""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Tentativa {retry_count + 1}/{max_retries} de conectar ao RabbitMQ...")
            
            # Tenta conectar
            connection = await aio_pika.connect_robust(
                RABBITMQ_URL,
                timeout=30,
                client_properties={
                    "connection_name": "queue-initializer"
                }
            )
            
            # Se chegou aqui, a conexão foi bem sucedida
            logger.info("Conectado ao RabbitMQ com sucesso")
            return connection
            
        except Exception as e:
            logger.warning(f"RabbitMQ ainda não está pronto: {str(e)}")
            retry_count += 1
            if retry_count >= max_retries:
                logger.error("Número máximo de tentativas excedido")
                raise
            await asyncio.sleep(2)
    
    raise Exception("Não foi possível conectar ao RabbitMQ após várias tentativas")

async def setup_queue():
    """Função principal para configurar a queue."""
    logger.info("Iniciando configuração da queue...")
    
    try:
        # Esperar RabbitMQ estar pronto
        connection = await wait_for_rabbitmq()
        channel = await connection.channel()
        
        # Criar a queue
        queue = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-delivery-limit": 3
            }
        )
        
        logger.info(f"Queue '{QUEUE_NAME}' criada com sucesso como Quorum Queue")
        
        # Manter a conexão aberta por um tempo para garantir que a queue foi criada
        await asyncio.sleep(5)
        
        # Fechar a conexão
        await connection.close()
        logger.info("Conexão fechada com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar queue: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(setup_queue())
    except KeyboardInterrupt:
        logger.info("Interrompido pelo utilizador")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        exit(1) 