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