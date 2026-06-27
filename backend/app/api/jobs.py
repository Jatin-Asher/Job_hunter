from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.core import get_db
from app.models.models import Job, Application, SavedJob, MatchScore, User
from app.schemas.schemas import JobWithMatch
from app.services.dependencies import get_current_user
from app.services.scraping_service import JobScrapingService
from app.workers.tasks import calculate_match_scores_task
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ============ SCHEMAS FOR SCRAPING ============

class ScrapeRequest(BaseModel):
    """Request schema for job scraping"""
    keywords: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    experience_level: Optional[List[str]] = None


class ScrapeResponse(BaseModel):
    """Response schema for scraping"""
    source: str
    jobs_found: int
    jobs_saved: int
    duplicates_skipped: int
    errors: List[str]
    sources: Dict[str, Dict] = Field(default_factory=dict)


# ============ SCRAPING ENDPOINTS ============

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs(
    request: ScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scrape jobs from all configured job platforms and save to database
    
    Args:
        request: Scrape request with keywords, locations, and experience level
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Scraping results with counts of jobs found, saved, and duplicates
    """
    try:
        scraper_service = JobScrapingService()
        result = scraper_service.scrape_all_sources(
            keywords=request.keywords,
            locations=request.locations,
            experience_level=request.experience_level,
            db=db
        )

        all_errors = []
        for source_result in result["sources"].values():
            all_errors.extend(source_result.get("errors", []))
        
        return ScrapeResponse(
            source="Multiple",
            jobs_found=result["total_jobs_found"],
            jobs_saved=result["total_jobs_saved"],
            duplicates_skipped=result["total_duplicates_skipped"],
            errors=all_errors,
            sources=result["sources"],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during scraping: {str(e)}"
        )


# ============ JOB LISTING ENDPOINTS ============

@router.get("/", response_model=List[JobWithMatch])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    keyword: str = Query("", min_length=0),
    location: str = Query("", min_length=0),
    source: str = Query("", min_length=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all jobs with filters"""
    
    query = db.query(Job).filter(Job.is_active == True)
    
    if keyword:
        query = query.filter(
            (Job.title.ilike(f"%{keyword}%")) | 
            (Job.company.ilike(f"%{keyword}%"))
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if source:
        query = query.filter(Job.source == source)
    
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get user's saved jobs and applications
    saved_job_ids = set(
        job_id for (job_id,) in db.query(SavedJob.job_id).filter(SavedJob.user_id == current_user.id).all()
    )
    applied_job_ids = set(
        job_id for (job_id,) in db.query(Application.job_id).filter(Application.user_id == current_user.id).all()
    )
    
    # Get match scores
    match_scores = db.query(MatchScore).filter(MatchScore.user_id == current_user.id).all()
    match_dict = {m.job_id: m.overall_score for m in match_scores}
    
    result = []
    for job in jobs:
        job_dict = {
            **job.__dict__,
            "match_score": match_dict.get(job.id),
            "is_saved": job.id in saved_job_ids,
            "is_applied": job.id in applied_job_ids
        }
        result.append(job_dict)
    
    return result


@router.get("/saved/list", response_model=List[JobWithMatch])
async def list_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List saved jobs"""

    saved_jobs = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    applied_job_ids = set(
        job_id for (job_id,) in db.query(Application.job_id).filter(Application.user_id == current_user.id).all()
    )
    match_scores = db.query(MatchScore).filter(MatchScore.user_id == current_user.id).all()
    match_dict = {m.job_id: m.overall_score for m in match_scores}

    jobs = []
    for saved_job in saved_jobs:
        if not saved_job.job:
            continue
        jobs.append({
            **saved_job.job.__dict__,
            "match_score": match_dict.get(saved_job.job_id),
            "is_saved": True,
            "is_applied": saved_job.job_id in applied_job_ids,
        })

    return jobs


@router.get("/{job_id}", response_model=JobWithMatch)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job details"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get match score
    match_score = db.query(MatchScore).filter(
        MatchScore.user_id == current_user.id,
        MatchScore.job_id == job_id
    ).first()
    
    # Check if saved
    is_saved = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first() is not None
    
    # Check if applied
    is_applied = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == job_id
    ).first() is not None
    
    return {
        **job.__dict__,
        "match_score": match_score.overall_score if match_score else None,
        "is_saved": is_saved,
        "is_applied": is_applied
    }


@router.post("/{job_id}/save")
async def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save job"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already saved
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already saved"
        )
    
    saved_job = SavedJob(user_id=current_user.id, job_id=job_id)
    db.add(saved_job)
    db.commit()

    # Calculate match score asynchronously. Saving the liked job must not depend
    # on Redis/Celery being available, so this runs after commit and failures are
    # intentionally non-fatal.
    try:
        calculate_match_scores_task.delay(current_user.id, job_id)
    except Exception:
        pass
    
    return {"message": "Job saved successfully"}


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsave job"""
    
    saved_job = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )
    
    db.delete(saved_job)
    db.commit()
    
    return {"message": "Job unsaved successfully"}

