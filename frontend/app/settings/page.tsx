'use client'

import React from 'react'
import { useProfile, useUpdateProfile } from '@/hooks/useApi'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { User } from '@/types'

export default function SettingsPage() {
  const { data: profileData } = useProfile()
  const updateProfile = useUpdateProfile()
  const { register, handleSubmit, reset } = useForm()

  React.useEffect(() => {
    if (profileData?.data) {
      reset({
        full_name: profileData.data.full_name,
        skills: profileData.data.skills?.join(', '),
        desired_roles: profileData.data.desired_roles?.join(', '),
        preferred_locations: profileData.data.preferred_locations?.join(', '),
      })
    }
  }, [profileData, reset])

  const onSubmit = async (data: any) => {
    const updateData = {
      full_name: data.full_name,
      skills: data.skills ? data.skills.split(',').map((s: string) => s.trim()) : [],
      desired_roles: data.desired_roles ? data.desired_roles.split(',').map((r: string) => r.trim()) : [],
      preferred_locations: data.preferred_locations ? data.preferred_locations.split(',').map((l: string) => l.trim()) : [],
    }

    updateProfile.mutate(updateData, {
      onSuccess: () => {
        toast.success('Profile updated successfully!')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Update failed')
      },
    })
  }

  return (
    <div className="max-w-2xl space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600">Manage your profile and preferences</p>
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg border border-slate-200 p-6 space-y-6">
        <h2 className="text-xl font-semibold text-slate-900">Profile Information</h2>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Full Name
          </label>
          <input
            type="text"
            {...register('full_name')}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Skills (comma-separated)
          </label>
          <textarea
            {...register('skills')}
            rows={3}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Python, JavaScript, React, Node.js"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Desired Roles (comma-separated)
          </label>
          <input
            type="text"
            {...register('desired_roles')}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Software Engineer, Data Scientist"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Preferred Locations (comma-separated)
          </label>
          <input
            type="text"
            {...register('preferred_locations')}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Remote, San Francisco, New York"
          />
        </div>

        <button
          type="submit"
          disabled={updateProfile.isPending}
          className="w-full bg-primary-600 text-white font-semibold py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </form>

      {/* Other Settings */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-6">
        <h2 className="text-xl font-semibold text-slate-900">Account Settings</h2>

        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-slate-900">Change Password</p>
            <p className="text-sm text-slate-600">Update your password regularly</p>
          </div>
          <button className="px-4 py-2 border border-slate-200 rounded-lg hover:bg-slate-50">
            Change
          </button>
        </div>

        <hr className="border-slate-200" />

        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-slate-900">Email Notifications</p>
            <p className="text-sm text-slate-600">Receive alerts about new jobs</p>
          </div>
          <input type="checkbox" className="h-5 w-5" defaultChecked />
        </div>

        <hr className="border-slate-200" />

        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-slate-900">Delete Account</p>
            <p className="text-sm text-slate-600">Permanently delete your account</p>
          </div>
          <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
