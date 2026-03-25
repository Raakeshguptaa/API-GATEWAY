# api-gateway

A lightweight reverse proxy built with Python. Handles auth, rate limiting, and request routing — no third-party gateway needed.

---

## Why I built this

Most API gateway solutions are either too heavy or too opinionated. This one is a single FastAPI app you can actually read and understand. Routes are defined in a YAML file, rate limits run on Redis, and everything forwards through `httpx`. That's it.

---

## What it does

- Routes incoming requests to downstream services based on `routes.yaml`
- Validates JWT tokens or API keys before forwarding
- Blocks clients that exceed request limits (sliding window via Redis)
- Attaches a unique ID to every request for tracing
- Logs every request/response with timing

---

## Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| HTTP client | httpx |
| Auth | PyJWT |
| Rate limiting | Redis |
| Route config | PyYAML |

---

## Project structure

```
api-gateway/
├── app/
│   ├── main.py                  # FastAPI app + middleware registration
│   ├── core/
│   │   ├── config.py            # Env vars and settings
│   │   └── logger.py            # Logging setup
│   ├── proxy/
│   │   ├── router.py            # Matches request path to route config
│   │   └── client.py            # Forwards request via httpx
│   ├── auth/
│   │   ├── jwt_handler.py       # JWT decode/verify
│   │   ├── api_key.py           # API key lookup
│   │   └── middleware.py        # Auth middleware
│   ├── rate_limit/
│   │   ├── limiter.py           # Sliding window logic
│   │   └── middleware.py        # Rate limit middleware
│   ├── middleware/
│   │   ├── request_id.py        # Injects X-Request-ID header
│   │   └── logging.py           # Request/response logger
│   └── routes/
│       ├── admin.py             # Manage routes and API keys
│       └── health.py            # GET /health
├── config/
│   └── routes.yaml              # Route definitions
├── tests/
│   ├── test_proxy.py
│   ├── test_auth.py
│   └── test_rate_limit.py
├── docker-compose.yml
├── Dockerfile
├── .env
└── requirements.txt
```

---

## Getting started

**Prerequisites:** Python 3.11+, Docker (for Redis)

```bash
git clone https://github.com/yourname/api-gateway.git
cd api-gateway
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Start Redis:
```bash
docker run -d -p 6379:6379 redis
```

Copy the env file and fill in your values:
```bash
cp .env.example .env
```

Run the gateway:
```bash
uvicorn app.main:app --reload --port 8000
```

---

## Defining routes

Edit `config/routes.yaml`:

```yaml
routes:
  - path: /api/users
    target: http://localhost:8001/users
    method: GET
    auth_required: true
    rate_limit:
      requests: 10
      window_seconds: 60

  - path: /api/orders
    target: http://localhost:8002/orders
    method: POST
    auth_required: true
    rate_limit:
      requests: 5
      window_seconds: 30
```

Routes are loaded at startup. Restart the server to pick up changes (hot-reload config support is on the roadmap).

---

## Testing rate limits

Spin up a dummy downstream service:

```python
# dummy_service.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def users():
    return {"data": ["Alice", "Bob"]}
```

```bash
uvicorn dummy_service:app --port 8001
```

Then hammer the gateway:

```python
# test_rate_limit.py
import httpx, time

for i in range(10):
    r = httpx.get("http://localhost:8000/api/users")
    print(f"Request {i+1}: {r.status_code}")
    time.sleep(0.1)
```

After hitting the limit you'll get:

```json
{
  "error": "Too Many Requests",
  "retry_after": "60 seconds"
}
```

You can also inspect the Redis state directly:

```bash
redis-cli ZCARD rate_limit:127.0.0.1:/api/users
```

---

## Environment variables

```
JWT_SECRET=your_secret_here
REDIS_HOST=localhost
REDIS_PORT=6379
ROUTES_CONFIG=config/routes.yaml
```

---

## Request flow

```
Client
  └─► Uvicorn
        └─► FastAPI
              ├─ Request ID middleware
              ├─ Logging middleware
              ├─ Auth middleware  (JWT / API key via PyJWT)
              ├─ Rate limit middleware  (sliding window via Redis)
              └─ Proxy router  (path match from routes.yaml)
                    └─► httpx  ──►  Downstream service
```

---

## Running tests

```bash
pytest tests/ -v
```

---

## Roadmap

- [ ] Hot-reload routes without restart
- [ ] Per-route auth bypass for public endpoints
- [ ] Dashboard UI for traffic monitoring
- [ ] gRPC forwarding support
- [ ] Prometheus metrics endpoint

---

## License

MIT