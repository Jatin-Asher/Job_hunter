from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.core import get_db
from app.models.models import Application, Job
from app.schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to a job"""
    
    job = db.query(Job).filter(Job.id == app_data.job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == app_data.job_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied to this job"
        )
    
    application = Application(
        user_id=current_user.id,
        job_id=app_data.job_id,
        status="applied"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    status_filter: str = Query("", min_length=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user applications"""
    
    query = db.query(Application).filter(Application.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Application.status == status_filter)
    
    applications = query.offset(skip).limit(limit).all()
    
    return applications


@router.get("/stats")
async def get_application_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application statistics"""
    
    total_applications = db.query(func.count(Application.id)).filter(
        Application.user_id == current_user.id
    ).scalar() or 0
    
    status_counts = db.query(
        Application.status,
        func.count(Application.id)
    ).filter(
        Application.user_id == current_user.id
    ).group_by(Application.status).all()
    
    status_dict = {status: count for status, count in status_counts}
    
    return {
        "total_applications": total_applications,
        "by_status": status_dict
    }


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application details"""
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: int,
    app_data: ApplicationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status"""
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application.status = app_data.status
    if app_data.notes:
        application.notes = app_data.notes
    
    db.commit()
    db.refresh(application)
    
    return application


@router.delete("/{app_id}")
async def delete_application(
    app_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete application"""
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
