from fastapi import APIRouter
from app.api.endpoints import auth, skills, jobs, employability

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(employability.router, prefix="/employability", tags=["Employability"])