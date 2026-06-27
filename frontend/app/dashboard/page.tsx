'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '@/services/api'
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import {
  Briefcase, TrendingUp, CheckCircle, Heart
} from 'lucide-react'

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => dashboardService.getStats(),
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading dashboard...</div>
  }

  const statsData = stats?.data

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600">Welcome back! Here's your job search overview.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Total Jobs Found</p>
              <p className="text-3xl font-bold text-slate-900">
                {statsData?.total_jobs_found || 0}
              </p>
            </div>
            <Briefcase className="h-10 w-10 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Applied</p>
              <p className="text-3xl font-bold text-slate-900">
                {statsData?.applied_jobs || 0}
              </p>
            </div>
            <TrendingUp className="h-10 w-10 text-green-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Saved Jobs</p>
              <p className="text-3xl font-bold text-slate-900">
                {statsData?.saved_jobs || 0}
              </p>
            </div>
            <Heart className="h-10 w-10 text-red-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Avg Match Score</p>
              <p className="text-3xl font-bold text-slate-900">
                {statsData?.average_match_score?.toFixed(1) || 0}%
              </p>
            </div>
            <CheckCircle className="h-10 w-10 text-primary-600 opacity-20" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Jobs by Source */}
        {statsData?.jobs_by_source && Object.keys(statsData.jobs_by_source).length > 0 && (
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Jobs by Source</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(statsData.jobs_by_source).map(([name, value]) => ({
                    name,
                    value,
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {[0, 1, 2, 3].map((index) => (
                    <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b', '#ef4444'][index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Application Funnel */}
        {statsData?.application_funnel && Object.keys(statsData.application_funnel).length > 0 && (
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Application Funnel</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(statsData.application_funnel).map(([name, value]) => ({
                name: name.replace(/_/g, ' ').toUpperCase(),
                count: value,
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Jobs by Location */}
        {statsData?.jobs_by_location && Object.keys(statsData.jobs_by_location).length > 0 && (
          <div className="bg-white rounded-lg border border-slate-200 p-6 lg:col-span-2">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Top Locations</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={Object.entries(statsData.jobs_by_location)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 10)
                  .map(([name, value]) => ({ name, value }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}
