'use client'

import { useEffect } from 'react'
import { useAuth } from '../providers'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    } else if (!authLoading && isAuthenticated) {
      router.push('/dashboard/home')
    }
  }, [isAuthenticated, authLoading, router])

  // Show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    </div>
  )
}