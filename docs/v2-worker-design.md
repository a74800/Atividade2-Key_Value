# V2 Worker Design

## Goal

Define the behavior and responsibilities of the Worker Service in the V2 architecture.

The worker is responsible for processing asynchronous commands received through RabbitMQ, ensuring reliability, idempotency, and correct state transitions.

---

# 1. Overview

The Worker Service consumes messages from RabbitMQ and executes operations such as PUT and DELETE.

It is responsible for:

- processing commands
- updating the database (CockroachDB)
- updating or invalidating cache (Redis)
- updating operation status
- handling retries and dead-letter queue logic

---

# 2. Command Message Structure

Each message sent to RabbitMQ represents a command.

## Example

```json
{
  "operationId": "op-123",
  "requestId": "req-456",
  "type": "PUT",
  "key": "user:1",
  "value": "Joao",
  "retryCount": 0,
  "timestamp": "2026-03-15T10:00:00Z"
}