from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database.core import get_db
from app.models.models import User
from app.schemas.schemas import UserProfile, UserProfileUpdate, UserResponse
from app.services.dependencies import get_current_user
import os

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    if profile_data.full_name:
        current_user.full_name = profile_data.full_name
    
    if profile_data.skills is not None:
        current_user.skills = profile_data.skills
    
    if profile_data.experience is not None:
        current_user.experience = profile_data.experience
    
    if profile_data.preferred_locations is not None:
        current_user.preferred_locations = profile_data.preferred_locations
    
    if profile_data.desired_roles is not None:
        current_user.desired_roles = profile_data.desired_roles
    
    if profile_data.salary_expectations is not None:
        current_user.salary_expectations = profile_data.salary_expectations
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload resume"""
    
    # In production, save to cloud storage (S3, etc.)
    # For now, just save filename
    filename = f"resume_{current_user.id}_{file.filename}"
    
    current_user.resume_url = f"/uploads/{filename}"
    db.commit()
    
    return {
        "message": "Resume uploaded successfully",
        "filename": filename
    }


@router.post("/upload-profile-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo"""
    
    # In production, save to cloud storage (S3, etc.)
    filename = f"profile_{current_user.id}_{file.filename}"
    
    current_user.profile_photo_url = f"/uploads/{filename}"
    db.commit()
    
    return {
        "message": "Profile photo uploaded successfully",
        "filename": filename
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
