'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ChatFallback() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to mentorship page if there's a routing issue
    router.push('/mentorship')
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Redirecting...</p>
      </div>
    </div>
  )
}
