'use client'

import React from 'react'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Bell, Menu, LogOut, Home, Briefcase, Heart, FileText, Settings } from 'lucide-react'

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-primary-600" />
          <span className="text-xl font-bold text-slate-900">JobHunter</span>
        </Link>

        {/* Desktop Navigation */}
        {isAuthenticated && (
          <nav className="hidden items-center gap-1 md:flex">
            <Link href="/dashboard" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
              <Home className="inline h-4 w-4 mr-1" /> Dashboard
            </Link>
            <Link href="/jobs" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
              <Briefcase className="inline h-4 w-4 mr-1" /> Jobs
            </Link>
            <Link href="/saved" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
              <Heart className="inline h-4 w-4 mr-1" /> Saved
            </Link>
            <Link href="/applications" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
              <FileText className="inline h-4 w-4 mr-1" /> Applications
            </Link>
          </nav>
        )}

        {/* Right Side */}
        <div className="flex items-center gap-4">
          {isAuthenticated && (
            <>
              <button className="relative p-2 text-slate-600 hover:text-primary-600">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
              </button>
              <Link href="/settings" className="p-2 text-slate-600 hover:text-primary-600">
                <Settings className="h-5 w-5" />
              </Link>
              <div className="flex items-center gap-2">
                <img
                  src={user?.profile_photo_url || 'https://via.placeholder.com/32'}
                  alt={user?.full_name}
                  className="h-8 w-8 rounded-full"
                />
                <button
                  onClick={logout}
                  className="p-2 text-slate-600 hover:text-red-600"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </>
          )}
          {!isAuthenticated && (
            <div className="flex gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                Sign In
              </Link>
              <Link
                href="/signup"
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
              >
                Sign Up
              </Link>
            </div>
          )}

          {/* Mobile Menu */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && isAuthenticated && (
        <nav className="border-t border-slate-200 bg-slate-50 p-4 md:hidden">
          <Link href="/dashboard" className="block px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
            Dashboard
          </Link>
          <Link href="/jobs" className="block px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
            Jobs
          </Link>
          <Link href="/saved" className="block px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
            Saved
          </Link>
          <Link href="/applications" className="block px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
            Applications
          </Link>
          <Link href="/settings" className="block px-3 py-2 text-sm font-medium text-slate-700 hover:text-primary-600">
            Settings
          </Link>
        </nav>
      )}
    </header>
  )
}
