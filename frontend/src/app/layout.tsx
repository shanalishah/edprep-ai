import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'IELTS Master Platform - AI-Powered Writing Assessment',
  description: 'Advanced IELTS writing preparation with AI-powered feedback, personalized learning, and comprehensive analytics.',
  keywords: 'IELTS, writing, assessment, AI, feedback, preparation, English, language learning',
  authors: [{ name: 'IELTS Master Platform' }],
  robots: 'index, follow',
  openGraph: {
    title: 'IELTS Master Platform - AI-Powered Writing Assessment',
    description: 'Advanced IELTS writing preparation with AI-powered feedback and personalized learning.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IELTS Master Platform - AI-Powered Writing Assessment',
    description: 'Advanced IELTS writing preparation with AI-powered feedback and personalized learning.',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
