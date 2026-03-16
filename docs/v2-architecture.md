# V2 Architecture

## Main goal

Redesign the distributed key-value system to improve robustness, observability, and distributed ownership logic.

## API style

The V2 API distinguishes between synchronous reads and asynchronous write commands.

### Read endpoint
- GET /keys/{key}

### Write command endpoints
- POST /commands/put
- POST /commands/delete

### Operation tracking endpoint
- GET /operations/{operationId}

Write commands return:
- 202 Accepted
- operationId

## Main services

- API Service
- Worker Service

## Infrastructure components

- RabbitMQ
- Redis
- CockroachDB
- NGINX
- HAProxy

## Operation lifecycle

1. Client submits command
2. API validates request
3. API creates operation record
4. API publishes message to RabbitMQ
5. Worker consumes message
6. Worker persists data in CockroachDB
7. Worker updates or invalidates Redis
8. Worker updates operation status

## Initial V2 features

- Request ID
- Operation ID
- Idempotency
- Retry with backoff
- Dead-letter queue
- Structured logging
- Metrics
- Key ownership (future extension)

## Read flow

1. Client sends GET /keys/{key}
2. API checks Redis cache
3. If key exists in Redis, return value
4. If key does not exist in Redis, query CockroachDB
5. If found in DB, return value and optionally refresh Redis cache

## Operation states

Possible operation states:
- ACCEPTED
- PROCESSING
- COMPLETED
- FAILED
- DEAD_LETTERED

## Consistency model

The V2 system remains eventually consistent for write operations, but exposes explicit operation tracking to make asynchronous behavior visible to clients.