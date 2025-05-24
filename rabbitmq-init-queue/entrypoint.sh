#!/bin/sh

echo "⏳ A aguardar que o cluster RabbitMQ esteja completo..."

# Aguarda que cada nó esteja a correr
for node in rabbitmq-node1 rabbitmq-node2 rabbitmq-node3; do
  until rabbitmqctl -n rabbit@$node status > /dev/null 2>&1; do
    echo "A esperar pelo $node..."
    sleep 5
  done
done

# Aguarda que o cluster tenha os três nós como running_nodes
until rabbitmqctl -n rabbit@rabbitmq-node1 cluster_status | grep -q 'running_nodes.\+rabbit@rabbitmq-node1.\+rabbit@rabbitmq-node2.\+rabbit@rabbitmq-node3'; do
  echo "A verificar cluster_status (ainda incompleto)..."
  sleep 5
done

# Aguarda que cada nó esteja pronto para aceitar conexões
for node in rabbitmq-node1 rabbitmq-node2 rabbitmq-node3; do
  until rabbitmqctl -n rabbit@$node list_connections > /dev/null 2>&1; do
    echo "A esperar que $node esteja pronto para aceitar conexões..."
    sleep 5
  done
done

# Aguarda mais um pouco para garantir que tudo está estável
echo "Aguardando estabilização do cluster..."
sleep 10

echo "Cluster completo com os 3 nós unidos e pronto."

# Corre o script Python que cria a fila quorum
python setup_queue.py
