## API style

The V2 API will use:
- GET for synchronous reads
- POST for asynchronous write commands

Reason:
The system uses RabbitMQ and worker-based asynchronous processing, so POST better reflects command submission than direct resource replacement.