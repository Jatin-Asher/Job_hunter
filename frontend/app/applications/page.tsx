'use client'

import React from 'react'
import { useApplications, useUpdateApplication } from '@/hooks/useApi'
import { Application } from '@/types'
import toast from 'react-hot-toast'
import { Trash2 } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  applied: 'bg-blue-100 text-blue-800',
  interview_scheduled: 'bg-purple-100 text-purple-800',
  technical_round: 'bg-indigo-100 text-indigo-800',
  hr_round: 'bg-orange-100 text-orange-800',
  offer_received: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export default function ApplicationsPage() {
  const [selectedStatus, setSelectedStatus] = React.useState('')
  const [skip, setSkip] = React.useState(0)
  const { data: applicationsData, isLoading } = useApplications(selectedStatus, skip, 10)
  const updateApplication = useUpdateApplication()

  const handleStatusChange = (appId: number, newStatus: string) => {
    updateApplication.mutate(
      { id: appId, data: { status: newStatus } },
      {
        onSuccess: () => {
          toast.success('Application updated!')
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Update failed')
        },
      }
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">My Applications</h1>
        <p className="text-slate-600">Track and manage your job applications</p>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        <button
          onClick={() => { setSelectedStatus(''); setSkip(0) }}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedStatus === ''
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}
        >
          All
        </button>
        {Object.keys(STATUS_COLORS).map((status) => (
          <button
            key={status}
            onClick={() => { setSelectedStatus(status); setSkip(0) }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedStatus === status
                ? 'bg-primary-600 text-white'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {status.replace(/_/g, ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-8 text-slate-500">Loading applications...</div>
        ) : applicationsData?.data && applicationsData.data.length > 0 ? (
          <>
            <div className="grid gap-4">
              {applicationsData.data.map((app: Application) => (
                <div
                  key={app.id}
                  className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-slate-900">Job #{app.job_id}</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[app.status]}`}>
                          {app.status.replace(/_/g, ' ')}
                        </span>
                      </div>
                      {app.notes && (
                        <p className="text-sm text-slate-600 mt-2">{app.notes}</p>
                      )}
                      <p className="text-xs text-slate-500 mt-2">
                        Applied: {new Date(app.created_at).toLocaleDateString()}
                      </p>
                    </div>

                    {/* Status Dropdown */}
                    <select
                      value={app.status}
                      onChange={(e) => handleStatusChange(app.id, e.target.value)}
                      className="px-3 py-2 border border-slate-200 rounded-lg text-sm"
                    >
                      {Object.keys(STATUS_COLORS).map((status) => (
                        <option key={status} value={status}>
                          {status.replace(/_/g, ' ')}
                        </option>
                      ))}
                    </select>

                    <button className="p-2 text-slate-400 hover:text-red-600">
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex justify-between gap-2 mt-6">
              <button
                onClick={() => setSkip(Math.max(0, skip - 10))}
                disabled={skip === 0}
                className="px-4 py-2 border border-slate-200 rounded-lg disabled:opacity-50 hover:bg-slate-50"
              >
                Previous
              </button>
              <span className="py-2 text-slate-600">
                Page {Math.floor(skip / 10) + 1}
              </span>
              <button
                onClick={() => setSkip(skip + 10)}
                className="px-4 py-2 border border-slate-200 rounded-lg hover:bg-slate-50"
              >
                Next
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-slate-500">
            No applications yet. Start applying to jobs!
          </div>
        )}
      </div>
    </div>
  )
}
