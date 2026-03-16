# V2 Retry and DLQ Strategy

## Goal

Improve reliability of asynchronous command processing by introducing bounded retries and a dead-letter queue.

---

## Main queue

- store-events

This queue receives new asynchronous commands submitted by the API.

---

## Dead-letter queue

- store-events.dlq

This queue stores messages that could not be processed successfully after the maximum number of retries.

---

## Retry policy

Each message includes a retry count.

Rules:

- if processing succeeds, mark operation as COMPLETED
- if processing fails due to a temporary error, increment retry count and retry
- if retry count exceeds the maximum allowed retries, send the message to DLQ
- if processing fails due to a permanent error, send the message directly to DLQ

---

## Maximum retries

Initial V2 policy:
- maxRetries = 3

---

## Temporary errors

Examples:
- database timeout
- Redis unavailable
- transient network issue

These errors should be retried.

---

## Permanent errors

Examples:
- invalid payload
- unsupported operation type
- malformed command
- deterministic application error

These errors should not be retried indefinitely.

---

## Operation status integration

The operations table must be updated as follows:

- ACCEPTED
- PROCESSING
- COMPLETED
- FAILED
- DEAD_LETTERED

retry_count is incremented whenever a retry occurs.

---

## Benefits

- avoids infinite retry loops
- isolates poison messages
- improves observability
- supports future manual or scheduled reprocessing