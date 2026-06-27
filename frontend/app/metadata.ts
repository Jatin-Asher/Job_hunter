import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Job Hunter - Find Your Perfect Job',
  description: 'AI-powered job matching platform for finding your dream job',
  keywords: ['jobs', 'career', 'employment', 'AI matching'],
  viewport: 'width=device-width, initial-scale=1',
  icons: {
    icon: '/favicon.ico',
  },
}

export { default } from './page'
