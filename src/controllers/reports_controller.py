from fastapi import APIRouter, HTTPException, Depends, status
from services.user_service import UserService
from repositories.user_repository import UserRepository
from config.db import get_database

router = APIRouter(prefix="/reports", tags=["Reports"])


async def get_user_service():
    """Dependency to get user service with database connection"""
    database = await get_database()
    user_repository = UserRepository(database)
    return UserService(user_repository)


@router.get("/university/{university_name}")
async def get_university_report(
    university_name: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get aggregated employability report for a university"""
    try:
        report = await user_service.get_university_report(university_name)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate university report: {str(e)}"
        )


@router.get("/analytics/overview")
async def get_analytics_overview(
    user_service: UserService = Depends(get_user_service)
):
    """Get general analytics overview"""
    try:
        # Get all users for general statistics
        all_users = await user_service.find_users()
        
        # Calculate basic statistics
        total_users = len(all_users)
        universities = list(set(user.university for user in all_users))
        careers = list(set(user.career for user in all_users))
        
        # Get sample scores for overview
        user_scores = []
        for user in all_users[:10]:  # Sample first 10 users
            score = await user_service.get_employability_score(str(user.id))
            if score:
                user_scores.append(score.overall_score)
        
        avg_score = sum(user_scores) / len(user_scores) if user_scores else 0
        
        return {
            "total_users": total_users,
            "total_universities": len(universities),
            "total_careers": len(careers),
            "average_employability_score": round(avg_score, 2),
            "top_universities": universities[:5],
            "top_careers": careers[:5]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics overview: {str(e)}"
        )