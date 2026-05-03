from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db        
from .routes import router

app = FastAPI(title="User Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(router, prefix="/api/v1", tags=["users"])

@app.get("/health")
def health():
    return {"status": "healthy", "service": "user-service", "version": "1.0.0"}