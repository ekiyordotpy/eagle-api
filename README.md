# eagle-api
Eagle Bank REST API

## Running locally

```bash
docker-compose -p eagle-api up --build -d
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

## Running tests

Spins up an isolated Postgres, runs pytest, then tears everything down:

```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Exit code mirrors pytest (0 = all passed).

