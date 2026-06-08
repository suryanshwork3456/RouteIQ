from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import admin, rider
from routers import tracking
# from routers import map_ws

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Logistics Hyper-Routing Engine Backend",
    version="1.0.0",
    description="Scalable decoupled routing platform supporting real-time tracking pipelines."
)

app.include_router(admin.router)
app.include_router(rider.router)

# Cross-Origin Resource Sharing handling configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this down explicitly for standard build environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Include Modular Sub-routers
app.include_router(tracking.router)
# app.include_router(map_ws.router)

@app.get("/")
async def root_health_check():
    return {"status": "healthy", "service": "Logistics Routing Core"}