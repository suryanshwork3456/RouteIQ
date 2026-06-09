# 🚚 Logistics Assignment Backend

Smart delivery assignment system built with FastAPI.
Assigns orders to riders using an **Efficiency Score** that weighs distance, batching, rating and busyness.

---

## Architecture

```
app/
├── main.py                        # FastAPI app + lifespan
├── worker.py                      # Celery beat tasks
├── core/
│   ├── config.py                  # Settings from .env
│   └── auth.py                    # JWT + password hashing
├── db/
│   ├── session.py                 # Async SQLAlchemy engine
│   └── redis_client.py            # Redis helpers + pub/sub
├── models/
│   └── models.py                  # SQLAlchemy ORM models
├── schemas/
│   └── schemas.py                 # Pydantic request/response models
├── services/
│   ├── distance_service.py        # Haversine + OSRM road distance
│   ├── batching_service.py        # DBSCAN order clustering
│   ├── scoring_service.py         # Efficiency score engine
│   ├── assignment_engine.py       # Orchestrates full assign cycle
│   └── rating_service.py          # Rolling avg rider ratings
├── api/routes/
│   ├── auth.py                    # POST /api/auth/register, /login
│   ├── orders.py                  # CRUD + status + manual trigger
│   ├── riders.py                  # Location, status, stats
│   ├── supermarkets.py            # CRUD
│   ├── ratings.py                 # Submit + summary
│   └── websockets.py              # WS /ws/rider/{id}, /ws/dashboard
└── utils/
    └── websocket_manager.py       # WS connection manager + Redis listener
```

---

## Efficiency Score Formula

```
Score = 0.40 × distance_score
      + 0.30 × batch_score
      + 0.20 × rating_score
      + 0.10 × busyness_score
```

| Component | Meaning |
|---|---|
| `distance_score` | `1 - (total_km / max_city_km)` — shorter route = higher |
| `batch_score` | `(batch_size - 1) / (MAX_BATCH - 1)` — more orders per trip = higher |
| `rating_score` | `(avg_stars - 1) / 4` — 5★ rider = 1.0 |
| `busyness_score` | `1 - (active / capacity)` — free rider = 1.0 |

Weights are configurable via `.env`.

---

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit DATABASE_URL, REDIS_URL, SECRET_KEY

# 3. Run services
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres
docker run -d -p 6379:6379 redis

# 4. Start API
uvicorn app.main:app --reload

# 5. Start Celery worker
celery -A app.worker.celery_app worker --loglevel=info

# 6. Start Celery beat (periodic assignment)
celery -A app.worker.celery_app beat --loglevel=info
```

---

## API Endpoints

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register rider |
| POST | `/api/auth/login` | Login → JWT token |

### Orders
| Method | Path | Description |
|---|---|---|
| POST | `/api/orders/` | Create order (auto-triggers assignment) |
| GET | `/api/orders/` | List orders (filter by status/rider/market) |
| GET | `/api/orders/{id}` | Get order details |
| PATCH | `/api/orders/{id}/status` | Update status (picked_up / delivered) |
| POST | `/api/orders/trigger-assignment` | Manual assignment cycle |

### Riders
| Method | Path | Description |
|---|---|---|
| GET | `/api/riders/` | List all riders |
| GET | `/api/riders/me` | My profile (auth required) |
| PATCH | `/api/riders/me/location` | Update GPS location |
| PATCH | `/api/riders/me/status` | Update status |
| GET | `/api/riders/{id}/stats` | Live stats + Redis counts |

### Supermarkets
| Method | Path | Description |
|---|---|---|
| POST | `/api/supermarkets/` | Add supermarket |
| GET | `/api/supermarkets/` | List active supermarkets |

### Ratings
| Method | Path | Description |
|---|---|---|
| POST | `/api/ratings/` | Submit star rating for delivered order |
| GET | `/api/ratings/rider/{id}` | Rider rating summary + breakdown |

### WebSocket
| Path | Description |
|---|---|
| `ws://host/ws/rider/{id}` | Rider app: send location/status, receive assignments |
| `ws://host/ws/dashboard` | Ops dashboard: receive all events live |

---

## WebSocket Message Format

**Rider → Server:**
```json
{"type": "location", "lat": 28.6139, "lon": 77.2090}
{"type": "status",   "status": "picked_up"}
```

**Server → Rider (assignment event):**
```json
{
  "event": "order_assigned",
  "batch_id": "uuid",
  "order_ids": [12, 13],
  "rider_id": 5,
  "score": 0.847
}
```
