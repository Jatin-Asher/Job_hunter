from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.core import get_db
from app.models.models import JobFilter
from app.schemas.schemas import JobFilterCreate, JobFilterUpdate, JobFilterResponse
from app.services.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/filters", tags=["filters"])


@router.post("/", response_model=JobFilterResponse)
async def create_filter(
    filter_data: JobFilterCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create job filter"""
    
    new_filter = JobFilter(
        user_id=current_user.id,
        name=filter_data.name,
        keywords=filter_data.keywords,
        experience_levels=filter_data.experience_levels,
        locations=filter_data.locations,
        work_modes=filter_data.work_modes,
        company_sizes=filter_data.company_sizes,
        salary_min=filter_data.salary_min,
        salary_max=filter_data.salary_max,
        date_posted=filter_data.date_posted,
        easy_apply_only=filter_data.easy_apply_only
    )
    
    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)
    
    return new_filter


@router.get("/", response_model=List[JobFilterResponse])
async def list_filters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's job filters"""
    
    filters = db.query(JobFilter).filter(
        JobFilter.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return filters


@router.get("/{filter_id}", response_model=JobFilterResponse)
async def get_filter(
    filter_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific filter"""
    
    job_filter = db.query(JobFilter).filter(
        JobFilter.id == filter_id,
        JobFilter.user_id == current_user.id
    ).first()
    
    if not job_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filter not found"
        )
    
    return job_filter


@router.put("/{filter_id}", response_model=JobFilterResponse)
async def update_filter(
    filter_id: int,
    filter_data: JobFilterUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update filter"""
    
    job_filter = db.query(JobFilter).filter(
        JobFilter.id == filter_id,
        JobFilter.user_id == current_user.id
    ).first()
    
    if not job_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filter not found"
        )
    
    # Update fields
    if filter_data.name is not None:
        job_filter.name = filter_data.name
    if filter_data.keywords is not None:
        job_filter.keywords = filter_data.keywords
    if filter_data.experience_levels is not None:
        job_filter.experience_levels = filter_data.experience_levels
    if filter_data.locations is not None:
        job_filter.locations = filter_data.locations
    if filter_data.work_modes is not None:
        job_filter.work_modes = filter_data.work_modes
    if filter_data.company_sizes is not None:
        job_filter.company_sizes = filter_data.company_sizes
    if filter_data.salary_min is not None:
        job_filter.salary_min = filter_data.salary_min
    if filter_data.salary_max is not None:
        job_filter.salary_max = filter_data.salary_max
    if filter_data.date_posted is not None:
        job_filter.date_posted = filter_data.date_posted
    if filter_data.easy_apply_only is not None:
        job_filter.easy_apply_only = filter_data.easy_apply_only
    if filter_data.is_active is not None:
        job_filter.is_active = filter_data.is_active
    
    db.commit()
    db.refresh(job_filter)
    
    return job_filter


@router.delete("/{filter_id}")
async def delete_filter(
    filter_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete filter"""
    
    job_filter = db.query(JobFilter).filter(
        JobFilter.id == filter_id,
        JobFilter.user_id == current_user.id
    ).first()
    
    if not job_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filter not found"
        )
    
    db.delete(job_filter)
    db.commit()
    
    return {"message": "Filter deleted successfully"}
