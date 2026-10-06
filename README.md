# Two-Stack Rewrite

Same spec, two implementations: **Go** and **Python/FastAPI**.

A task manager REST API built twice to compare how the same problems are solved in different runtimes.

## Spec

- `GET /healthz` → health check
- `GET /tasks` → list tasks
- `POST /tasks` → create task
- `GET /tasks/:id` → get task
- `PATCH /tasks/:id` → update task
- `DELETE /tasks/:id` → delete task
- In-memory storage (thread-safe)
- Request logging middleware
- Graceful shutdown

## Quick Start

### Go

```bash
cd go
go run main.go
# Server on :8080
```

### Python

```bash
cd python
pip install -r requirements.txt
python main.py
# Server on :8080
```

## Comparison

See [COMPARISON.md](COMPARISON.md) for detailed analysis.

## Quick Summary

| | Go | Python |
|---|---|---|
| Lines | 180 | 130 |
| Dependencies | 0 | 3 |
| Concurrency | goroutines + mutex | asyncio + async/await |
| Validation | manual | Pydantic |
| Docs | manual | auto (`/docs`) |
| Deploy | single binary | container/venv |

## License

MIT — see [LICENSE](LICENSE).