from celery import shared_task
from app.workers.celery_app import celery_app
from app.database.core import SessionLocal
from app.models.models import ScrapingLog, User, MatchScore, Job, Notification
from app.services.scraping_service import JobScrapingService
from app.services.matching_engine import AIMatchingEngine
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="scrape_jobs_task")
def scrape_jobs_task(filters: dict):
    """Async task to scrape jobs"""
    db = SessionLocal()
    start_time = datetime.utcnow()
    scraping_log = None
    
    try:
        scraping_log = ScrapingLog(
            source="Multiple",
            status="in_progress",
            started_at=start_time
        )
        db.add(scraping_log)
        db.commit()
        
        service = JobScrapingService()
        results = service.scrape_all_sources(
            keywords=filters.get("keywords", []),
            locations=filters.get("locations", []),
            experience_level=filters.get("experience_level"),
            db=db,
        )
        errors = []
        for source_result in results["sources"].values():
            errors.extend(source_result.get("errors", []))
        
        scraping_log.jobs_found = results["total_jobs_found"]
        scraping_log.jobs_saved = results["total_jobs_saved"]
        scraping_log.duplicates_skipped = results["total_duplicates_skipped"]
        scraping_log.status = "success" if not errors else "partial"
        scraping_log.error_message = "\n".join(errors) if errors else None
        scraping_log.completed_at = datetime.utcnow()
        scraping_log.duration = (scraping_log.completed_at - start_time).seconds
        
        db.commit()
        
        return {
            "status": "success",
            "jobs_found": results["total_jobs_found"],
            "jobs_saved": results["total_jobs_saved"],
            "duplicates_skipped": results["total_duplicates_skipped"],
            "sources": results["sources"],
        }
        
    except Exception as e:
        logger.error(f"Scraping task error: {str(e)}")
        if scraping_log:
            scraping_log.status = "failed"
            scraping_log.error_message = str(e)
            scraping_log.completed_at = datetime.utcnow()
            db.commit()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="calculate_match_scores_task")
def calculate_match_scores_task(user_id: int, job_id: int):
    """Calculate match score for a user-job pair"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not user or not job:
            return {"status": "error", "message": "User or job not found"}
        
        # Get user resume (placeholder - would come from cloud storage)
        resume_text = " ".join(user.skills) + " " + str(user.experience)
        
        # Calculate match
        engine = AIMatchingEngine()
        match_data = engine.calculate_match_score(
            resume_text,
            job.description,
            user.skills if user.skills else [],
            job.skills_required if job.skills_required else []
        )
        
        # Save or update match score
        existing_match = db.query(MatchScore).filter(
            MatchScore.user_id == user_id,
            MatchScore.job_id == job_id
        ).first()
        
        if existing_match:
            existing_match.overall_score = match_data["overall_score"]
            existing_match.skills_match = match_data["skills_match"]
            existing_match.missing_skills = match_data["missing_skills"]
            existing_match.strength_areas = match_data["strength_areas"]
            existing_match.weak_areas = match_data["weak_areas"]
            existing_match.explanation = match_data["explanation"]
        else:
            match_score = MatchScore(
                user_id=user_id,
                job_id=job_id,
                overall_score=match_data["overall_score"],
                skills_match=match_data["skills_match"],
                missing_skills=match_data["missing_skills"],
                strength_areas=match_data["strength_areas"],
                weak_areas=match_data["weak_areas"],
                explanation=match_data["explanation"]
            )
            db.add(match_score)
        
        db.commit()
        
        # Trigger notification if high match
        if match_data["overall_score"] >= 75:
            send_match_notification_task.delay(user_id, job_id, match_data["overall_score"])
        
        return {
            "status": "success",
            "match_score": match_data["overall_score"]
        }
        
    except Exception as e:
        logger.error(f"Match calculation error: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="send_match_notification_task")
def send_match_notification_task(user_id: int, job_id: int, match_score: float):
    """Send notification for high match jobs"""
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        notification = Notification(
            user_id=user_id,
            title="High Match Job Found!",
            message=f"{job.title} at {job.company} matches your profile {match_score}%",
            notification_type="new_job"
        )
        db.add(notification)
        db.commit()
        
    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
    
    finally:
        db.close()


@celery_app.task(name="scheduled_scraping_task")
def scheduled_scraping_task():
    """Scheduled task to scrape jobs periodically"""
    db = SessionLocal()
    
    try:
        # Get all active users with filters
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            filters = db.query(JobFilter).filter(
                JobFilter.user_id == user.id,
                JobFilter.is_active == True
            ).all()
            
            for filter_obj in filters:
                filter_dict = {
                    "keywords": filter_obj.keywords,
                    "experience_levels": filter_obj.experience_levels,
                    "locations": filter_obj.locations,
                    "work_modes": filter_obj.work_modes,
                    "company_sizes": filter_obj.company_sizes,
                    "salary_min": filter_obj.salary_min,
                    "salary_max": filter_obj.salary_max,
                    "date_posted": filter_obj.date_posted,
                    "easy_apply_only": filter_obj.easy_apply_only
                }
                
                scrape_jobs_task.delay(filter_dict)
        
        return {"status": "success", "message": "Scheduled scraping started"}
        
    except Exception as e:
        logger.error(f"Scheduled scraping error: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()
