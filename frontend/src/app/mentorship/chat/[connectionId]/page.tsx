'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter, useParams } from 'next/navigation'

interface Message {
  id: number
  connection_id: number
  sender_id: number
  message_type: 'text' | 'file' | 'image' | 'audio' | 'video' | 'system'
  content: string
  file_url?: string
  file_name?: string
  file_size?: number
  is_read: boolean
  read_at?: string
  is_edited: boolean
  edited_at?: string
  created_at: string
  sender?: {
    id: number
    username: string
    full_name: string
    email: string
    role: string
  }
}

interface Connection {
  id: number
  mentor_id: number
  mentee_id: number
  status: 'pending' | 'active' | 'completed' | 'cancelled'
  connection_message: string
  goals: string[]
  target_band_score: number
  focus_areas: string[]
  mentor: {
    id: number
    username: string
    full_name: string
    email: string
    role: string
  }
  mentee: {
    id: number
    username: string
    full_name: string
    email: string
    role: string
  }
  created_at: string
}

export default function ChatPage() {
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const router = useRouter()
  const params = useParams()
  
  const [connectionId, setConnectionId] = useState<string | null>(null)
  const [connection, setConnection] = useState<Connection | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const maxRetries = 3

  // Extract connection ID from URL
  useEffect(() => {
    const id = params.connectionId as string
    if (id && id !== 'undefined' && id !== 'null') {
      setConnectionId(id)
    }
  }, [params.connectionId])

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  // Fetch data when authenticated and connection ID is available
  useEffect(() => {
    if (isAuthenticated && connectionId && connectionId !== 'undefined' && connectionId !== 'null') {
      setLoading(true)
      setError(null)
      fetchConnection()
      fetchMessages()
    }
  }, [isAuthenticated, connectionId])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchConnection = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found. Please log in again.')
        setLoading(false)
        return
      }
      
      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setConnection(data.connection)
        setRetryCount(0)
      } else {
        const raw = await response.text().catch(() => '')
        let detail = ''
        try { detail = JSON.parse(raw)?.detail ?? raw } catch { detail = raw || `${response.status} ${response.statusText}` }
        setError(`Failed to load connection details: ${detail}`)
      }
    } catch (error: any) {
      console.error('Error fetching connection:', error)
      setError(`Failed to load connection details: ${error.message || 'Please try again.'}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found. Please log in again.')
        return
      }

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
        setRetryCount(0)
      } else {
        const raw = await response.text().catch(() => '')
        let detail = ''
        try { detail = JSON.parse(raw)?.detail ?? raw } catch { detail = raw || `${response.status} ${response.statusText}` }
        setError(`Failed to load messages: ${detail}`)
      }
    } catch (error: any) {
      console.error('Error fetching messages:', error)
      setError(`Failed to load messages: ${error.message || 'Please try again.'}`)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    setSending(true)
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found. Please log in again.')
        setSending(false)
        return
      }

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Bearer ${token}`
        },
        body: new URLSearchParams({
          content: newMessage.trim(),
          message_type: 'text'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, data.data])
        setNewMessage('')
      } else {
        const raw = await response.text().catch(() => '')
        let detail = ''
        try { detail = JSON.parse(raw)?.detail ?? raw } catch { detail = raw || `${response.status} ${response.statusText}` }
        setError(`Failed to send message: ${detail}`)
      }
    } catch (error: any) {
      console.error('Error sending message:', error)
      setError(`Failed to send message: ${error.message || 'Please try again.'}`)
    } finally {
      setSending(false)
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const handleRetry = () => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1)
      setError(null)
      fetchConnection()
      fetchMessages()
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user || !connection) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
          <p className="text-sm text-gray-500 mt-2">Connection ID: {connectionId}</p>
        </div>
      </div>
    )
  }

  const isMentor = user.role === 'mentor' || user.role === 'tutor'
  const otherUser = isMentor ? connection.mentee : connection.mentor

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.back()}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Chat with {otherUser.full_name}
                </h1>
                <p className="text-sm text-gray-500">
                  {connection.status === 'active' ? 'Active' : connection.status}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-4 mt-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
              {retryCount < maxRetries && (
                <button
                  onClick={handleRetry}
                  className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                >
                  Retry ({retryCount}/{maxRetries})
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow-sm border h-96 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading messages...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender_id === user.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender_id === user.id ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {formatTime(message.created_at)}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="mt-4 flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={sending}
          />
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim() || sending}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}