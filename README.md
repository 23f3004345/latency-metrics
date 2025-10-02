# latency-metrics

A Vercel Python endpoint that analyzes telemetry data and returns per-region metrics.

## API Endpoint

### POST /api/index.py

Accepts a JSON request body with the following structure:

```json
{
  "regions": ["amer", "emea"],
  "threshold_ms": 179
}
```

Returns per-region metrics:
- `avg_latency`: Mean latency in milliseconds
- `p95_latency`: 95th percentile latency in milliseconds
- `avg_uptime`: Mean uptime as a percentage (0-100)
- `breaches`: Count of records where latency exceeds the threshold

Example response:

```json
{
  "amer": {
    "avg_latency": 162,
    "p95_latency": 214.0,
    "avg_uptime": 99.2,
    "breaches": 2
  },
  "emea": {
    "avg_latency": 150,
    "p95_latency": 204.0,
    "avg_uptime": 99.2,
    "breaches": 1
  }
}
```

## CORS

The endpoint supports CORS for POST requests from any origin.