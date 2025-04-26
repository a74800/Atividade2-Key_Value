#!/bin/bash

URL="http://localhost:8080/store"  # Endpoint correto
NUM_REQUESTS=20                    # Número de pedidos que queres enviar

for i in $(seq 1 $NUM_REQUESTS)
do
  echo "Enviando pedido $i..."

  curl -X PUT "$URL" \
    -H "accept: */*" \
    -H "Content-Type: application/json" \
    -d "{\"key\":\"chave_$i\", \"value\":\"valor_$i\"}"

  echo ""  # Linha em branco para separar as respostas
  sleep 0.2  # Pausa de 200ms entre pedidos para não ser demasiado agressivo
done

echo "Todos os pedidos foram enviados!"
