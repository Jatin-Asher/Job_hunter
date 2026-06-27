'use client'

import React, { useState } from 'react'
import Header from '@/components/Header'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

export default function Providers({
  children,
}: {
  children: React.ReactNode
}) {
  const [queryClient] = useState(
    () => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5, // 5 minutes
          gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
        },
      },
    })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <Header />
      <main className="container mx-auto py-6">
        {children}
      </main>
      <Toaster position="bottom-right" />
    </QueryClientProvider>
  )
}
