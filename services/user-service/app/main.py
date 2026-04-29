from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import os

app = FastAPI(
    title="User Service",
    description="Authentication and User Management Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["users"])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {"message": "User Service API"}
