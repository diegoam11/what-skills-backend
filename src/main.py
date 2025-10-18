from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.db import connect_to_mongo, close_mongo_connection
from .controllers.auth_controller import router as auth_router
from .controllers.user_controller import router as user_router
from .controllers.employability_controller import router as employability_router
from .controllers.reports_controller import router as reports_router

from src.controllers.user_controller import router as user_router

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(employability_router)
app.include_router(reports_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection"""
    await close_mongo_connection()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "WhatSkills API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "WhatSkills API",
        "version": "1.0.0"
    }
