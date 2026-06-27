'use client'

import React from 'react'
import { useAuthStore } from '@/lib/store'
import { useAuth } from '@/hooks/useAuth'
import Link from 'next/link'
import { ArrowRight, Briefcase, BarChart3, Zap, Users } from 'lucide-react'

export default function LandingPage() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return null // Redirect to dashboard for authenticated users
  }

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="py-20 text-center space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold text-slate-900">
          Find Your Perfect Job
          <br />
          <span className="text-primary-600">Effortlessly</span>
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
          AI-powered job matching that finds opportunities tailored to your skills,
          experience, and preferences. Stop searching, start applying.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/signup"
            className="px-8 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 flex items-center gap-2"
          >
            Get Started <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            href="/login"
            className="px-8 py-3 border border-slate-300 text-slate-900 rounded-lg font-semibold hover:bg-slate-50"
          >
            Sign In
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 space-y-12">
        <h2 className="text-4xl font-bold text-center text-slate-900">
          Why Choose JobHunter?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 bg-white rounded-lg border border-slate-200">
            <Zap className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="font-semibold text-slate-900 mb-2">AI Matching</h3>
            <p className="text-slate-600">
              Get matched with jobs based on your skills and experience.
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg border border-slate-200">
            <BarChart3 className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="font-semibold text-slate-900 mb-2">Track Progress</h3>
            <p className="text-slate-600">
              Monitor your applications with our powerful tracking dashboard.
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg border border-slate-200">
            <Briefcase className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="font-semibold text-slate-900 mb-2">Multiple Sources</h3>
            <p className="text-slate-600">
              Search jobs from LinkedIn, Indeed, Naukri, and more.
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg border border-slate-200">
            <Users className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="font-semibold text-slate-900 mb-2">Community</h3>
            <p className="text-slate-600">
              Join thousands of job seekers finding success.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 space-y-12">
        <h2 className="text-4xl font-bold text-center text-slate-900">
          How It Works
        </h2>
        <div className="space-y-6">
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Create Profile</h3>
              <p className="text-slate-600">Upload your resume and configure your job preferences.</p>
            </div>
          </div>
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Set Filters</h3>
              <p className="text-slate-600">Define your ideal job criteria - location, role, salary, etc.</p>
            </div>
          </div>
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Get Matched</h3>
              <p className="text-slate-600">Our AI finds jobs matching your profile and sends notifications.</p>
            </div>
          </div>
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              4
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Apply & Track</h3>
              <p className="text-slate-600">Apply to jobs and track your applications in one place.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800 text-white rounded-lg text-center space-y-6">
        <h2 className="text-4xl font-bold">Ready to Find Your Dream Job?</h2>
        <p className="text-lg opacity-90 max-w-2xl mx-auto">
          Join thousands of job seekers who've already found success with JobHunter.
        </p>
        <Link
          href="/signup"
          className="inline-block px-8 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-slate-100"
        >
          Get Started Free
        </Link>
      </section>
    </div>
  )
}
