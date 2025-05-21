#!/bin/bash

HOST="haproxy"
PORT=26256

echo "⏳ A aguardar $HOST:$PORT..."

# Espera até o serviço responder na porta
until (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1; do
  sleep 1
done

echo "✅ $HOST:$PORT disponível, a iniciar aplicação..."
exec java -jar app.jar
