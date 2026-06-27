'use client'

import React from 'react'
import { useJobs, useCreateApplication, useScrapeAllPlatformJobs } from '@/hooks/useApi'
import JobCard from '@/components/JobCard'
import { Download, Filter, Loader2, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import { Job } from '@/types'

const JOBS_LIMIT = 5000

export default function JobsPage() {
  const [keyword, setKeyword] = React.useState('')
  const [location, setLocation] = React.useState('')
  const [source, setSource] = React.useState('')
  const [showFilters, setShowFilters] = React.useState(false)

  const { data: jobsData, isLoading } = useJobs(0, JOBS_LIMIT, keyword, location, source)
  const createApplication = useCreateApplication()
  const scrapeAllPlatformJobs = useScrapeAllPlatformJobs()

  const handleApply = (jobId: number) => {
    createApplication.mutate(jobId, {
      onSuccess: () => {
        toast.success('Applied to job successfully!')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to apply')
      },
    })
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
  }

  const handleScrape = () => {
    const keywords = keyword
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean)
    const locations = location
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean)

    scrapeAllPlatformJobs.mutate(
      { keywords, locations },
      {
        onSuccess: ({ data }) => {
          const sourceSummary = Object.values(data.sources || {})
            .map((sourceResult) => `${sourceResult.source}: ${sourceResult.jobs_saved} saved`)
            .join(', ')
          toast.success(
            `Entry-level scrape complete: ${data.jobs_saved} saved, ${data.duplicates_skipped} duplicates skipped.${sourceSummary ? ` (${sourceSummary})` : ''}`
          )
          if (data.errors.length > 0) {
            toast.error(data.errors[0])
          }
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Failed to scrape jobs')
        },
      }
    )
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex flex-col gap-2 lg:flex-row">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
            <input
              type="text"
              placeholder="Job title, keywords..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            <Filter className="h-5 w-5" />
            Filters
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
          >
            Search
          </button>
          <button
            type="button"
            onClick={handleScrape}
            disabled={scrapeAllPlatformJobs.isPending}
            className="flex items-center justify-center gap-2 px-5 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed font-medium"
          >
            {scrapeAllPlatformJobs.isPending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Download className="h-5 w-5" />
            )}
            {scrapeAllPlatformJobs.isPending ? 'Scraping...' : 'Scrape Entry-Level Jobs'}
          </button>
        </div>

        <div className={showFilters ? 'grid gap-3 md:grid-cols-2' : ''}>
          <input
            type="text"
            placeholder="Location, country, remote..."
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          {showFilters && (
            <select
              value={source}
              onChange={(event) => {
                setSource(event.target.value)
              }}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg bg-white text-slate-600"
            >
              <option value="">All platforms</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Remotive">Remotive</option>
              <option value="Arbeitnow">Arbeitnow</option>
              <option value="RemoteOK">RemoteOK</option>
            </select>
          )}
        </div>
      </form>

      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-8 text-slate-500">Loading jobs...</div>
        ) : jobsData?.data && jobsData.data.length > 0 ? (
          <>
            <p className="text-sm text-slate-500">
              Showing {jobsData.data.length} distinct scraped jobs. Use the search, location, and platform filters above to narrow results.
            </p>
            {jobsData.data.map((job: Job) => (
              <JobCard
                key={job.id}
                job={job}
                onApply={handleApply}
              />
            ))}
          </>
        ) : (
          <div className="text-center py-8 text-slate-500">
            No jobs found. Try adjusting your search filters.
          </div>
        )}
      </div>
    </div>
  )
}
