Perfeito. Vamos avançar para a **estrutura Java da V2**.

Agora o objetivo é fazer a ponte entre:

* documentação
* arquitetura
* implementação real

Ainda não vamos escrever o código completo, mas vamos definir **as packages, classes e responsabilidades** para os dois serviços:

* **API Service**
* **Worker Service**

Isto é importante para não misturares tudo quando começares a programar.

---

# 1. Visão geral da estrutura

Como vamos ter dois serviços, eu recomendo esta organização no repositório:

```text
services/
├── api-service/
└── worker-service/
```

Cada serviço terá o seu projeto Java separado.

---

# 2. Estrutura do `api-service`

Cria mentalmente algo deste género:

```text
api-service/
└── src/main/java/pt/joaosousa/apiservice/
    ├── ApiServiceApplication.java
    │
    ├── controller/
    │   ├── KeyController.java
    │   ├── CommandController.java
    │   └── OperationController.java
    │
    ├── service/
    │   ├── KeyQueryService.java
    │   ├── CommandService.java
    │   ├── OperationService.java
    │   ├── RequestIdService.java
    │   └── OperationIdService.java
    │
    ├── publisher/
    │   └── CommandPublisher.java
    │
    ├── repository/
    │   ├── KeyValueRepository.java
    │   └── OperationRepository.java
    │
    ├── model/
    │   ├── entity/
    │   │   ├── KeyValueEntity.java
    │   │   └── OperationEntity.java
    │   │
    │   ├── dto/
    │   │   ├── PutCommandRequest.java
    │   │   ├── DeleteCommandRequest.java
    │   │   ├── CommandAcceptedResponse.java
    │   │   ├── KeyValueResponse.java
    │   │   └── OperationStatusResponse.java
    │   │
    │   └── message/
    │       └── CommandMessage.java
    │
    ├── config/
    │   ├── RabbitConfig.java
    │   └── RedisConfig.java
    │
    └── exception/
        ├── GlobalExceptionHandler.java
        ├── ResourceNotFoundException.java
        └── QueueUnavailableException.java
```

---

# 3. Responsabilidade de cada parte do `api-service`

## `controller/`

Recebe pedidos HTTP.

### `KeyController`

Responsável por:

* `GET /keys/{key}`

### `CommandController`

Responsável por:

* `POST /commands/put`
* `POST /commands/delete`

### `OperationController`

Responsável por:

* `GET /operations/{operationId}`

Os controllers **não devem ter lógica pesada**.

---

## `service/`

### `KeyQueryService`

Lógica de leitura:

* consultar Redis
* fallback para CockroachDB
* refresh opcional de cache

### `CommandService`

Lógica de submissão de comandos:

* validar
* gerar IDs
* criar operação
* publicar mensagem

### `OperationService`

Gerir operações:

* criar registo
* consultar estado

### `RequestIdService`

Gerar `requestId`

### `OperationIdService`

Gerar `operationId`

---

## `publisher/`

### `CommandPublisher`

Responsável por publicar mensagens no RabbitMQ.

Isto é importante porque separa:

* lógica de negócio
* lógica de messaging

---

## `repository/`

### `KeyValueRepository`

Acesso à tabela `key_value_store`

### `OperationRepository`

Acesso à tabela `operations`

Se usares Spring Data JPA, isto fica bastante simples.

---

## `model/entity/`

### `KeyValueEntity`

Representa a tabela das keys

### `OperationEntity`

Representa a tabela das operações

---

## `model/dto/`

DTOs para entrada e saída da API.

Exemplo:

* `PutCommandRequest`
* `CommandAcceptedResponse`

Isto evita usar entidades diretamente nos endpoints.

---

## `model/message/`

### `CommandMessage`

Representa a mensagem enviada para RabbitMQ.

Vai ser o contrato entre:

* API Service
* Worker Service

---

# 4. Estrutura do `worker-service`

Agora o worker.

```text
worker-service/
└── src/main/java/pt/joaosousa/workerservice/
    ├── WorkerServiceApplication.java
    │
    ├── listener/
    │   └── CommandListener.java
    │
    ├── service/
    │   ├── WorkerProcessingService.java
    │   ├── CommandExecutionService.java
    │   ├── OperationService.java
    │   ├── RetryService.java
    │   ├── DlqService.java
    │   └── CacheService.java
    │
    ├── repository/
    │   ├── KeyValueRepository.java
    │   └── OperationRepository.java
    │
    ├── model/
    │   ├── entity/
    │   │   ├── KeyValueEntity.java
    │   │   └── OperationEntity.java
    │   │
    │   └── message/
    │       └── CommandMessage.java
    │
    ├── config/
    │   ├── RabbitConfig.java
    │   └── RedisConfig.java
    │
    ├── policy/
    │   └── RetryPolicy.java
    │
    └── exception/
        ├── PermanentProcessingException.java
        └── TemporaryProcessingException.java
```

---

# 5. Responsabilidade de cada parte do `worker-service`

## `listener/`

### `CommandListener`

Escuta o RabbitMQ.

Responsável por:

* receber a mensagem
* chamar o serviço de processamento

Não deve conter toda a lógica.

---

## `service/`

### `WorkerProcessingService`

Coordena o processamento completo:

* verificar operação
* mudar estado
* executar comando
* tratar erros
* decidir retry / DLQ

### `CommandExecutionService`

Executa a lógica real do comando:

* PUT
* DELETE

### `OperationService`

Atualiza estados:

* `PROCESSING`
* `COMPLETED`
* `FAILED`
* `DEAD_LETTERED`

### `RetryService`

Decide:

* republicar
* incrementar retry count

### `DlqService`

Envia mensagens para a DLQ

### `CacheService`

Atualiza/invalida Redis

---

## `policy/`

### `RetryPolicy`

Encapsula regras como:

* `maxRetries = 3`
* erro temporário vs permanente

---

## `exception/`

### `TemporaryProcessingException`

Erro que deve permitir retry

### `PermanentProcessingException`

Erro que deve ir para DLQ

Isto ajuda muito a manter a lógica limpa.

---

# 6. Classes principais mínimas

Se quiseres começar simples, eu começaria por estas.

## API Service — mínimo viável

* `CommandController`
* `OperationController`
* `CommandService`
* `OperationService`
* `CommandPublisher`
* `OperationEntity`
* `CommandMessage`

## Worker Service — mínimo viável

* `CommandListener`
* `WorkerProcessingService`
* `CommandExecutionService`
* `OperationService`
* `RetryService`
* `DlqService`
* `CommandMessage`

---

# 7. Fluxo entre classes

## No API Service

```text
CommandController
   ↓
CommandService
   ↓
OperationService
   ↓
CommandPublisher
   ↓
RabbitMQ
```

---

## No Worker Service

```text
RabbitMQ
   ↓
CommandListener
   ↓
WorkerProcessingService
   ↓
CommandExecutionService
   ↓
OperationService
   ↓
RetryService / DlqService
```

---

# 8. O que eu faria agora

Antes de escreveres código, eu documentaria isto também.

Cria:

```text
docs/v2-java-structure.md
```

e coloca lá a estrutura dos dois serviços e a responsabilidade das classes.

---

# 9. Conteúdo para `docs/v2-java-structure.md`

```md
# V2 Java Structure

## Goal

Define the Java package structure and main class responsibilities for the V2 distributed key-value system.

The V2 system is split into two main services:

- API Service
- Worker Service

---

# 1. API Service

## Main responsibility

Expose HTTP endpoints, handle synchronous reads, accept asynchronous write commands, create operation records, and publish commands to RabbitMQ.

## Suggested package structure

- controller
- service
- publisher
- repository
- model.entity
- model.dto
- model.message
- config
- exception

## Main classes

### Controller layer
- KeyController
- CommandController
- OperationController

### Service layer
- KeyQueryService
- CommandService
- OperationService
- RequestIdService
- OperationIdService

### Messaging
- CommandPublisher

### Repositories
- KeyValueRepository
- OperationRepository

### Models
- KeyValueEntity
- OperationEntity
- PutCommandRequest
- DeleteCommandRequest
- CommandAcceptedResponse
- KeyValueResponse
- OperationStatusResponse
- CommandMessage

---

# 2. Worker Service

## Main responsibility

Consume RabbitMQ commands, execute operations, update database and cache, and apply retry / DLQ logic.

## Suggested package structure

- listener
- service
- repository
- model.entity
- model.message
- config
- policy
- exception

## Main classes

### Listener layer
- CommandListener

### Service layer
- WorkerProcessingService
- CommandExecutionService
- OperationService
- RetryService
- DlqService
- CacheService

### Repositories
- KeyValueRepository
- OperationRepository

### Models
- KeyValueEntity
- OperationEntity
- CommandMessage

### Policy
- RetryPolicy

### Exceptions
- TemporaryProcessingException
- PermanentProcessingException

---

# 3. Main Design Principles

- controllers only handle HTTP
- services contain business logic
- repositories access persistence
- publishers handle RabbitMQ publishing
- listeners consume RabbitMQ messages
- retry and DLQ logic are isolated from command execution
- shared message contract must remain stable between services
```

---

# 10. O próximo passo que eu recomendo

Agora eu já passava para algo mais prático:

## definir o `CommandMessage`

Porque ele é o contrato partilhado entre:

* API
* Worker

E isso vai ajudar-te logo a começar implementação.

Se quiseres, no próximo passo eu dou-te já:

* o conteúdo do `docs/v2-command-contract.md`
* e a classe Java `CommandMessage` inicial.
