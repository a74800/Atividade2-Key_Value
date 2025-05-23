# Key-Value Store Distribuído

Este projeto consiste numa aplicação de armazenamento **chave-valor distribuída**, desenvolvida no âmbito da unidade curricular de **Sistemas Paralelos e Distribuídos**.

A aplicação segue uma arquitetura baseada em **microserviços**, integrando:

* **API REST em Spring Boot**
* **Cache distribuída com Redis Cluster**
* **Sistema de mensagens assíncronas com RabbitMQ Cluster**
* **Persistência distribuída com CockroachDB**
* **Balanceamento de carga com NGINX e HAProxy**
* **Execução e orquestração com Docker e Docker Compose**


## Arquitetura

```mermaid
graph TD
  Client -->|HTTP GET / PUT / DELETE| Nginx["Nginx (Load Balancer)"]

    Nginx --> API["API"]


  API -- GET cache --> Redis["Redis"]
  Redis -- cache miss --> CockroachDBLB

    API -- PUT / DELETE --> RabbitMQLB["RabbitMQ LB (HAProxy)"]
    RabbitMQLB --> RabbitMQ["RabbitMQ"]


    RabbitMQLB -- consume --> Worker["Worker"]


  Worker -- write --> CockroachDBLB["CockroachDB LB (HAProxy)"]
  CockroachDBLB --> CockroachDB["CockroachDB"]

  Worker -- update --> Redis
``` 

### Componentes:

* **NGINX**: Entrada das requisições (porta 8000)
* **Spring Boot APIs** (`api-1`, `api-2`, `api-3`): Expõem endpoints REST (`PUT`, `GET`, `DELETE`)
* **Redis Cluster** (6 nós): Armazenamento temporário chave-valor
* **RabbitMQ Cluster** (3 nós): Comunicação assíncrona com quorum queues
* **Consumers Python** (3 instâncias): Tratam as mensagens e gravam dados
* **CockroachDB** (3 nós): Base de dados relacional distribuída
* **HAProxy**: Balanceador interno (DB e RabbitMQ)

---

## Manual da API

O manual interativo da API (Swagger UI) pode ser acedido em:  
[`http://localhost:8000/swagger-ui/index.html`](http://localhost:8000/swagger-ui/index.html)


### `PUT /store`

```json
{
    "key": "exemplo",
    "value": "valor123"
}
```
---

### `GET /store/exemplo`

```json
{
    "value": "valor123"
}
```

---

### `DELETE /store/exemplo`

HTTP Response Code

---

## Instalação e Utilização

### Requisitos

* Docker e Docker Compose
* GNU/Linux

### Como correr

```bash
git clone https://github.com/a74800/Atividade2-Key_Value
cd Atividade2-Key_Value
chmod +x start.sh
./start.sh
```

* API disponível em: `http://localhost:8000/store/`
* Painel RabbitMQ: `http://localhost:15672` (guest / guest)
* CockroachDB UI: `http://localhost:8080`

---

## Capacidades

| Componente    | Capacidade                                  |
| ------------- | ------------------------------------------- |
| Redis Cluster | 3 shards com 3 réplicas (6 nós no total)    |
| RabbitMQ      | 3 nós com filas tipo quorum                 |
| CockroachDB   | 3 nós com replicação automática             |
| APIs          | Escaláveis horizontalmente (N x instâncias) |
| Balanceamento | NGINX externo + HAProxy interno             |

---

## Testes de Carga

Executado com a ferramenta `jmeter`:


---

## 📚 Bibliografia e Apoio

* [Docker](https://docs.docker.com/)
* [Spring Boot](https://spring.io/)
* [Redis Cluster](https://redis.io/)
* [RabbitMQ](https://www.rabbitmq.com/)
* [CockroachDB](https://www.cockroachlabs.com/)
* Parte da documentação e código teve apoio de modelos de linguagem IA (ChatGPT)
