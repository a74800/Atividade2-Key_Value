#!/bin/bash

# Nome da stack
STACK_NAME="mystack"

echo "========================"
echo "  Parando a stack: $STACK_NAME"
echo "========================"
docker stack rm $STACK_NAME

echo "Aguarde 10 segundos para a stack ser removida..."
sleep 10

echo "========================"
echo "  Saindo do Docker Swarm"
echo "========================"
docker swarm leave --force

echo "========================"
echo "  Stack parada e Swarm terminado!"
echo "========================"
