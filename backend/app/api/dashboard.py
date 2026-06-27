from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.core import get_db
from app.models.models import (
    User, Job, Application, SavedJob, MatchScore, ScrapingLog,
    JobFilter, Notification
)
from app.schemas.schemas import DashboardStats, ScrapingLogResponse
from app.services.dependencies import get_current_admin_user, get_current_user
from typing import List

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    
    # Total jobs found
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    
    # New jobs today
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    new_today = db.query(func.count(Job.id)).filter(
        func.DATE(Job.created_at) == today
    ).scalar() or 0
    
    # User's applied jobs
    applied_jobs = db.query(func.count(Application.id)).filter(
        Application.user_id == current_user.id
    ).scalar() or 0
    
    # User's saved jobs
    saved_jobs = db.query(func.count(SavedJob.id)).filter(
        SavedJob.user_id == current_user.id
    ).scalar() or 0
    
    # Average match score
    avg_match = db.query(func.avg(MatchScore.overall_score)).filter(
        MatchScore.user_id == current_user.id
    ).scalar() or 0.0
    
    # Jobs by location
    jobs_by_location = db.query(
        Job.location,
        func.count(Job.id)
    ).group_by(Job.location).limit(10).all()
    
    # Jobs by experience level
    jobs_by_exp = db.query(
        Job.experience_level,
        func.count(Job.id)
    ).group_by(Job.experience_level).all()
    
    # Jobs by source
    jobs_by_source = db.query(
        Job.source,
        func.count(Job.id)
    ).group_by(Job.source).all()
    
    # Application funnel
    app_funnel = db.query(
        Application.status,
        func.count(Application.id)
    ).filter(
        Application.user_id == current_user.id
    ).group_by(Application.status).all()
    
    return {
        "total_jobs_found": total_jobs,
        "new_jobs_today": new_today,
        "applied_jobs": applied_jobs,
        "saved_jobs": saved_jobs,
        "average_match_score": float(avg_match),
        "jobs_by_location": {loc or "Unknown": count for loc, count in jobs_by_location},
        "jobs_by_experience_level": {level or "Unknown": count for level, count in jobs_by_exp},
        "jobs_by_source": {source or "Unknown": count for source, count in jobs_by_source},
        "application_funnel": {status or "Unknown": count for status, count in app_funnel}
    }


# ============ ADMIN ENDPOINTS ============

@router.get("/admin/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at
        }
        for u in users
    ]


@router.get("/admin/jobs")
async def list_jobs_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all jobs (admin only)"""
    
    jobs = db.query(Job).offset(skip).limit(limit).all()
    
    return jobs


@router.get("/admin/scraping-logs")
async def list_scraping_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List scraping logs (admin only)"""
    
    logs = db.query(ScrapingLog).order_by(
        ScrapingLog.started_at.desc()
    ).offset(skip).limit(limit).all()
    
    return logs


@router.get("/admin/analytics")
async def get_analytics(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform analytics (admin only)"""
    
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    total_applications = db.query(func.count(Application.id)).scalar() or 0
    total_matches = db.query(func.count(MatchScore.id)).scalar() or 0
    
    # Average match score
    avg_match = db.query(func.avg(MatchScore.overall_score)).scalar() or 0.0
    
    # Users by plan (if we had plans)
    active_users = db.query(func.count(User.id)).filter(
        User.is_active == True
    ).scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_matches": total_matches,
        "average_match_score": float(avg_match)
    }
