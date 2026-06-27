from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ AUTH SCHEMAS ============

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    profile_photo_url: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ USER PROFILE SCHEMAS ============

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[Dict[str, Any]] = None
    preferred_locations: Optional[List[str]] = None
    desired_roles: Optional[List[str]] = None
    salary_expectations: Optional[Dict[str, Any]] = None


class UserProfile(UserResponse):
    skills: List[str]
    experience: Dict[str, Any]
    preferred_locations: List[str]
    desired_roles: List[str]
    salary_expectations: Dict[str, Any]


# ============ JOB FILTER SCHEMAS ============

class JobFilterCreate(BaseModel):
    name: str
    keywords: List[str] = []
    experience_levels: List[str] = []
    locations: List[str] = []
    work_modes: List[str] = []
    company_sizes: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    date_posted: str = "24 Hours"
    easy_apply_only: bool = False


class JobFilterUpdate(BaseModel):
    name: Optional[str] = None
    keywords: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    work_modes: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    date_posted: Optional[str] = None
    easy_apply_only: Optional[bool] = None
    is_active: Optional[bool] = None


class JobFilterResponse(BaseModel):
    id: int
    name: str
    keywords: List[str]
    experience_levels: List[str]
    locations: List[str]
    work_modes: List[str]
    company_sizes: List[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    date_posted: str
    easy_apply_only: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ JOB SCHEMAS ============

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_level: Optional[str] = None
    work_mode: Optional[str] = None
    company_size: Optional[str] = None
    description: str
    skills_required: List[str] = []
    apply_url: str
    company_logo_url: Optional[str] = None
    source: str
    posted_date: Optional[datetime] = None


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    experience_level: Optional[str]
    work_mode: Optional[str]
    company_size: Optional[str]
    description: str
    skills_required: List[str]
    apply_url: str
    company_logo_url: Optional[str]
    source: str
    posted_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class JobWithMatch(JobResponse):
    match_score: Optional[float] = None
    is_saved: bool = False
    is_applied: bool = False


# ============ APPLICATION SCHEMAS ============

class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationUpdate(BaseModel):
    status: str = Field(..., pattern="^(applied|interview_scheduled|technical_round|hr_round|offer_received|rejected)$")
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ MATCH SCORE SCHEMAS ============

class MatchScoreResponse(BaseModel):
    id: int
    overall_score: float
    skills_match: Dict[str, float]
    missing_skills: List[str]
    strength_areas: List[str]
    weak_areas: List[str]
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ NOTIFICATION SCHEMAS ============

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ DASHBOARD SCHEMAS ============

class DashboardStats(BaseModel):
    total_jobs_found: int
    new_jobs_today: int
    applied_jobs: int
    saved_jobs: int
    average_match_score: float
    jobs_by_location: Dict[str, int]
    jobs_by_experience_level: Dict[str, int]
    jobs_by_source: Dict[str, int]
    application_funnel: Dict[str, int]


# ============ SCRAPING LOG SCHEMAS ============

class ScrapingLogResponse(BaseModel):
    id: int
    source: str
    jobs_found: int
    jobs_saved: int
    duplicates_skipped: int
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]

    class Config:
        from_attributes = True
