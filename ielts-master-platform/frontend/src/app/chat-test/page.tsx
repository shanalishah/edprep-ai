'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function ChatTestPage() {
  const router = useRouter()
  const [connectionId, setConnectionId] = useState('1')

  const handleTestChat = () => {
    console.log('Testing chat with connection ID:', connectionId)
    router.push(`/mentorship/chat/${connectionId}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-xl font-semibold mb-4">Chat Test Page</h1>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Connection ID
            </label>
            <input
              type="text"
              value={connectionId}
              onChange={(e) => setConnectionId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter connection ID"
            />
          </div>
          <button
            onClick={handleTestChat}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Test Chat
          </button>
          <button
            onClick={() => router.push('/mentorship')}
            className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to Mentorship
          </button>
        </div>
      </div>
    </div>
  )
}



