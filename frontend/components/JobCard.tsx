'use client'

import React from 'react'
import { Job } from '@/types'
import { Heart, Share2, ExternalLink } from 'lucide-react'
import { useSaveJob, useUnsaveJob } from '@/hooks/useApi'
import toast from 'react-hot-toast'

interface JobCardProps {
  job: Job
  onApply: (jobId: number) => void
}

export default function JobCard({ job, onApply }: JobCardProps) {
  const saveJob = useSaveJob()
  const unsaveJob = useUnsaveJob()
  const [isSaved, setIsSaved] = React.useState(job.is_saved || false)

  const handleSave = () => {
    if (isSaved) {
      unsaveJob.mutate(job.id, {
        onSuccess: () => {
          setIsSaved(false)
          toast.success('Job removed from saved jobs')
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Failed to unsave job')
        },
      })
    } else {
      saveJob.mutate(job.id, {
        onSuccess: () => {
          setIsSaved(true)
          toast.success('Job saved successfully')
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Failed to save job')
        },
      })
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 hover:shadow-lg transition-shadow">
      <div className="flex gap-4">
        {/* Company Logo */}
        {job.company_logo_url && (
          <img
            src={job.company_logo_url}
            alt={job.company}
            className="h-12 w-12 rounded object-cover"
          />
        )}

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900 truncate">
                {job.title}
              </h3>
              <p className="text-sm text-slate-600">{job.company}</p>
            </div>

            {/* Match Score */}
            {job.match_score && (
              <div className="flex-shrink-0 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {job.match_score}%
                </div>
                <div className="text-xs text-slate-500">Match</div>
              </div>
            )}
          </div>

          {/* Details */}
          <div className="mt-2 flex flex-wrap gap-2 text-sm text-slate-600">
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
              {job.source}
            </span>
            <span>{job.location}</span>
            {job.work_mode && <span>•</span>}
            {job.work_mode && <span>{job.work_mode}</span>}
            {job.salary && <span>•</span>}
            {job.salary && <span className="font-medium text-slate-900">{job.salary}</span>}
          </div>

          {/* Skills */}
          {job.skills_required && job.skills_required.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {job.skills_required.slice(0, 3).map((skill) => (
                <span
                  key={skill}
                  className="inline-block bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-medium"
                >
                  {skill}
                </span>
              ))}
              {job.skills_required.length > 3 && (
                <span className="inline-block text-xs text-slate-500 px-2 py-1">
                  +{job.skills_required.length - 3} more
                </span>
              )}
            </div>
          )}

          {/* Description Preview */}
          <p className="mt-2 line-clamp-2 text-sm text-slate-600">
            {job.description}
          </p>

          {/* Actions */}
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => onApply(job.id)}
              disabled={job.is_applied}
              className="flex-1 bg-primary-600 text-white font-medium py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {job.is_applied ? 'Applied' : 'Apply Now'}
            </button>
            <button
              onClick={handleSave}
              disabled={saveJob.isPending || unsaveJob.isPending}
              className={`p-2 rounded-lg border ${
                isSaved
                  ? 'border-red-300 bg-red-50 text-red-600'
                  : 'border-slate-200 bg-white text-slate-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              aria-label={isSaved ? 'Unsave job' : 'Save job'}
            >
              <Heart className={`h-5 w-5 ${isSaved ? 'fill-current' : ''}`} />
            </button>
            {job.apply_url && (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                aria-label="Open job on source platform"
              >
                <ExternalLink className="h-5 w-5" />
              </a>
            )}
            <button className="p-2 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50">
              <Share2 className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
