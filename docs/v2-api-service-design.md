# V2 API Service Design

## Goal

Define the responsibilities and behavior of the API Service in the V2 architecture.

The API Service is responsible for:

- receiving HTTP requests from clients
- validating request payloads
- handling synchronous reads
- accepting asynchronous write commands
- creating operation records
- publishing commands to RabbitMQ
- exposing operation status to clients

---

# 1. Overview

The API Service is the public entry point of the distributed key-value system.

It supports two categories of operations:

- synchronous reads
- asynchronous write commands

This separation reflects the internal architecture of the system, where reads are handled directly and writes are processed asynchronously through RabbitMQ and workers.

---

# 2. Main Responsibilities

The API Service is responsible for:

- handling `GET /keys/{key}`
- handling `POST /commands/put`
- handling `POST /commands/delete`
- handling `GET /operations/{operationId}`
- generating `requestId`
- generating `operationId`
- storing operation metadata
- publishing command messages to RabbitMQ

The API Service is not responsible for:

- executing writes directly in CockroachDB
- processing retry logic
- consuming RabbitMQ messages
- moving messages to DLQ

These responsibilities belong to the Worker Service.

---

# 3. Endpoints

## 3.1 GET /keys/{key}

### Purpose

Retrieve the current value associated with a key.

### Request

`GET /keys/{key}`

### Processing flow

1. Receive request
2. Generate `requestId` (if not provided)
3. Check Redis cache
4. If found:
   - return value immediately
5. If not found:
   - query CockroachDB
6. If found in DB:
   - return value
   - optionally refresh Redis cache
7. If not found:
   - return `404`

### Responses

#### 200 OK

```json
{
  "key": "user:1",
  "value": "Joao"
}