#!/bin/bash

set -e

# Cores ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sem cor

# Função para hyperlinks ANSI (funciona em terminais que suportam)
function link() {
    printf "\e]8;;$1\e\\$2\e]8;;\e\\"
}

echo -e "\n${BLUE}[INFO] A iniciar sistema distribuído...${NC}\n"

# Verificações
for cmd in docker "docker compose"; do
    if ! $cmd version &> /dev/null; then
        echo -e "${RED}[ERRO] Comando '$cmd' não está disponível. Por favor instala e tenta novamente.${NC}"
        exit 1
    fi
done

# Construção e arranque
echo -e "${YELLOW}[INFO] Construindo imagens Docker...${NC}"
docker compose build

echo -e "${YELLOW}[INFO] A subir containers...${NC}"
docker compose up -d

# Hiperligações
API_URL="http://localhost:8000"
SWAGGER_URL="http://localhost:8000/swagger-ui/index.html"

echo -e "\n${GREEN}[SUCESSO] Sistema iniciado com sucesso!${NC}"
echo -e "API: $(link "$API_URL" "$API_URL")"
echo -e "Swagger: $(link "$SWAGGER_URL" "$SWAGGER_URL")"
echo -e "${BLUE}[INFO] Alguns serviços podem demorar alguns segundos a estar prontos.${NC}"
echo -e "${YELLOW}[PARAR O SISTEMA]:${NC} docker compose down"
echo -e ""
