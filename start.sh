#!/bin/bash

# Nome da stack
STACK_NAME="mystack"

echo "========================"
echo "  Limpando stack antiga"
echo "========================"
docker stack rm $STACK_NAME

# Esperar 10 segundos para garantir limpeza total
echo "Aguarde 10 segundos para limpeza total..."
sleep 10

echo "========================"
echo "  Inicializando Swarm"
echo "========================"
docker swarm init || echo "Swarm já estava ativo"

echo "========================"
echo "  Construindo imagens locais"
echo "========================"
docker compose -f stack.yml build

echo "========================"
echo "  Deploy da Stack: $STACK_NAME"
echo "========================"
docker stack deploy -c stack.yml $STACK_NAME

echo "========================"
echo "  Serviços atualmente ativos:"
echo "========================"
docker stack services $STACK_NAME
