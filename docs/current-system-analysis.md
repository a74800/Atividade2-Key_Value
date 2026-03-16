
# Current System Analysis

Version: Draft v1
Last updated: 2026-03-14

## Goal

Understand the current architecture, request flows, guarantees, and limitations of the existing distributed key-value system before redesigning it.

The objective is to identify strengths, weaknesses, and architectural decisions that should be improved in V2.

---

# Current Architecture

## Main Components

Client
↓
NGINX
↓
Spring Boot API (multiple instances)
↓
RabbitMQ Cluster
↓
Worker Consumers
↓
CockroachDB
↑
Redis Cluster (cache layer)

Components used:

- NGINX (load balancer)
- Spring Boot API
- RabbitMQ (asynchronous messaging)
- Redis (cache layer)
- CockroachDB (distributed persistence)
- Python workers

---

# Request Flow Analysis

## GET Flow

Step-by-step description of a GET request.

1. Client sends GET request to the API.
2. Request passes through NGINX load balancer.
3. API checks Redis cache for the key.
4. If key exists in Redis:
   - return value immediately.
5. If key does not exist in Redis:
   - query CockroachDB.
6. If found in DB:
   - return value.
   - store value in Redis cache.

Questions:

- What happens if Redis is unavailable?
- What happens if CockroachDB is slow?
- Is there a timeout strategy?

- If Redis is unavailable, the API should try to read directly from CockroachDB.
- If CockroachDB is slow, cache misses may result in high-latency responses.
- A timeout strategy should exist to prevent the API from waiting indefinitely on slow dependencies.

---

## PUT Flow

Step-by-step description of a PUT request.

1. Client sends PUT request to API.
2. API publishes message to RabbitMQ queue.
3. API returns response to client.
4. Worker consumes message.
5. Worker writes value to CockroachDB.
6. Worker updates Redis cache.

Questions:

- Is the operation synchronous or asynchronous?
- When does the write become visible to GET?
- What happens if RabbitMQ is unavailable?
- What happens if the worker crashes?
- Can the message be processed twice?

- The operation is asynchronous.
- The write becomes visible only after the worker persists the data and updates the cache.
- If RabbitMQ is unavailable, the write command should fail instead of being accepted.
- If the worker crashes, messages may remain pending until processing resumes.
- Yes, messages may potentially be processed more than once if retries occur and idempotency is not enforced.

---

## DELETE Flow

Step-by-step description of DELETE request.

1. Client sends DELETE request to API.
2. API publishes delete event to RabbitMQ.
3. Worker consumes message.
4. Worker deletes record from CockroachDB.
5. Worker invalidates Redis cache entry.

Questions:

- Is deletion synchronous?
- Can stale values remain in cache?

# Current System Analysis

## Goal

Understand the current architecture, request flows, guarantees, and limitations of the existing distributed key-value system before redesigning it.

The objective is to identify strengths, weaknesses, and architectural decisions that should be improved in V2.

---

# Current Architecture

## Main Components

Client
↓
NGINX
↓
Spring Boot API (multiple instances)
↓
RabbitMQ Cluster
↓
Worker Consumers
↓
CockroachDB
↑
Redis Cluster (cache layer)

Components used:

- NGINX (load balancer)
- Spring Boot API
- RabbitMQ (asynchronous messaging)
- Redis (cache layer)
- CockroachDB (distributed persistence)
- Python workers

---

# Request Flow Analysis

## GET Flow

Step-by-step description of a GET request.

1. Client sends GET request to the API.
2. Request passes through NGINX load balancer.
3. API checks Redis cache for the key.
4. If key exists in Redis:
   - return value immediately.
5. If key does not exist in Redis:
   - query CockroachDB.
6. If found in DB:
   - return value.
   - store value in Redis cache.

Questions:

- What happens if Redis is unavailable?
- What happens if CockroachDB is slow?
- Is there a timeout strategy?

- If Redis is unavailable, the API should try to read directly from CockroachDB.
- If CockroachDB is slow, cache misses may result in high-latency responses.
- A timeout strategy should exist to prevent the API from waiting indefinitely on slow dependencies.

---

## PUT Flow

Step-by-step description of a PUT request.

1. Client sends PUT request to API.
2. API publishes message to RabbitMQ queue.
3. API returns response to client.
4. Worker consumes message.
5. Worker writes value to CockroachDB.
6. Worker updates Redis cache.

Questions:

- Is the operation synchronous or asynchronous?
- When does the write become visible to GET?
- What happens if RabbitMQ is unavailable?
- What happens if the worker crashes?
- Can the message be processed twice?

- The operation is asynchronous.
- The write becomes visible only after the worker persists the data and updates the cache.
- If RabbitMQ is unavailable, the write command should fail instead of being accepted.
- If the worker crashes, messages may remain pending until processing resumes.
- Yes, messages may potentially be processed more than once if retries occur and idempotency is not enforced.

---

## DELETE Flow

Step-by-step description of DELETE request.

1. Client sends DELETE request to API.
2. API publishes delete event to RabbitMQ.
3. Worker consumes message.
4. Worker deletes record from CockroachDB.
5. Worker invalidates Redis cache entry.

Questions:

- Is deletion synchronous?
- Can stale values remain in cache?

---

# Consistency Model

Describe the current consistency guarantees.

Questions to answer:

- Is the system strongly consistent?
- Is it eventually consistent?
- Can stale reads occur?
- Are writes immediately visible?


- Deletion is asynchronous in the current architecture.
- Yes, stale values may temporarily remain visible until the worker deletes the record and invalidates the cache.

# Consistency Model

The system follows an eventually consistent model.

Writes are processed asynchronously through RabbitMQ and workers. Because of this, a write operation may not be immediately visible to subsequent reads.

Consistency characteristics:

- The system is not strongly consistent.
- Writes are not immediately visible.
- Stale reads may occur until the worker processes the message.
- Cache entries may temporarily contain outdated values until they are updated or invalidated.

However, once the worker processes the message and updates CockroachDB and Redis, the system converges to a consistent state.

---

# Failure Scenarios

What happens when these components fail?
## Redis failure

Expected behavior:

If Redis becomes unavailable, the API should still be able to read data directly from CockroachDB.

In this scenario:
- cache performance benefits are lost
- read latency may increase
- the system should remain functional if CockroachDB is healthy

Redis failures mainly affect performance rather than data correctness.


## RabbitMQ failure

Expected behavior:

If RabbitMQ is unavailable, the API may be unable to submit write operations to the queue.

In this case:
- PUT and DELETE operations should fail
- the API should return an error instead of pretending the operation was accepted

RabbitMQ availability is critical for write operations in the current architecture.

## CockroachDB failure

Expected behavior:

If CockroachDB becomes unavailable:

- workers cannot persist new writes
- reads that miss the cache cannot retrieve data
- the system may serve cached values if they exist in Redis

However, the system cannot guarantee fresh data without database availability.

## Worker failure

Expected behavior:

If worker processes crash or stop consuming messages:

- write and delete operations accumulate in RabbitMQ queues
- persistence to CockroachDB is delayed
- Redis cache may become outdated

Once workers recover, queued messages should be processed.

---

# Strengths of Current System

Examples:

- asynchronous messaging
- caching layer
- distributed persistence
- containerized deployment
- load balancing

(To be expanded)

---

# Weaknesses of Current System

Examples:

- lack of idempotency
- unclear retry strategy
- limited observability
- dependency on external components for distribution

(To be expanded)

---

# Consistency Model

Describe the current consistency guarantees.

Questions to answer:

- Is the system strongly consistent?
- Is it eventually consistent?
- Can stale reads occur?
- Are writes immediately visible?




---

# Failure Scenarios

What happens when these components fail?

## Redis failure

Expected behavior:
(To be filled)

## RabbitMQ failure

Expected behavior:
(To be filled)

## CockroachDB failure

Expected behavior:
(To be filled)

## Worker failure

Expected behavior:
(To be filled)

---

# Strengths of Current System

Examples:

- asynchronous messaging
- caching layer
- distributed persistence
- containerized deployment
- load balancing

(To be expanded)

---

# Weaknesses of Current System

Examples:

- lack of idempotency
- unclear retry strategy
- limited observability
- dependency on external components for distribution

(To be expanded)