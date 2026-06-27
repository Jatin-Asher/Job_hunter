import React from 'react'
import Providers from '@/components/Providers'
import './globals.css'

export const metadata = {
  title: 'JobHunter - AI-Powered Job Hunting',
  description: 'Find your perfect job with AI-powered matching',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}