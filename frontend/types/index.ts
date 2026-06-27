export interface User {
  id: number
  email: string
  username: string
  full_name: string
  profile_photo_url?: string
  is_verified: boolean
  created_at: string
  skills: string[]
  experience: Record<string, any>
  preferred_locations: string[]
  desired_roles: string[]
  salary_expectations: Record<string, any>
}

export interface Job {
  id: number
  title: string
  company: string
  location: string
  salary?: string
  salary_min?: number
  salary_max?: number
  experience_level?: string
  work_mode?: string
  company_size?: string
  description: string
  skills_required: string[]
  apply_url: string
  company_logo_url?: string
  source: string
  posted_date?: string
  created_at: string
  match_score?: number
  is_saved?: boolean
  is_applied?: boolean
}

export interface ScrapeJobsRequest {
  keywords?: string[]
  locations?: string[]
  experience_level?: string[]
}

export interface ScrapeJobsResponse {
  source: string
  jobs_found: number
  jobs_saved: number
  duplicates_skipped: number
  errors: string[]
  sources: Record<
    string,
    {
      source: string
      jobs_found: number
      jobs_saved: number
      duplicates_skipped: number
      errors: string[]
    }
  >
}

export interface JobFilter {
  id: number
  name: string
  keywords: string[]
  experience_levels: string[]
  locations: string[]
  work_modes: string[]
  company_sizes: string[]
  salary_min?: number
  salary_max?: number
  date_posted: string
  easy_apply_only: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Application {
  id: number
  job_id: number
  user_id: number
  status: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface MatchScore {
  id: number
  overall_score: number
  skills_match: Record<string, number>
  missing_skills: string[]
  strength_areas: string[]
  weak_areas: string[]
  explanation: string
  created_at: string
}

export interface DashboardStats {
  total_jobs_found: number
  new_jobs_today: number
  applied_jobs: number
  saved_jobs: number
  average_match_score: number
  jobs_by_location: Record<string, number>
  jobs_by_experience_level: Record<string, number>
  jobs_by_source: Record<string, number>
  application_funnel: Record<string, number>
}
