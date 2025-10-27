'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter, useParams } from 'next/navigation'
import { supabase } from '../../../../lib/supabaseClient'

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
  
  // Multiple ways to get connection ID for maximum reliability
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

  // Robust connection ID extraction
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Method 1: From URL params
      const urlParams = new URLSearchParams(window.location.search)
      const idFromQuery = urlParams.get('connectionId')
      
      // Method 2: From pathname
      const pathParts = window.location.pathname.split('/')
      const idFromPath = pathParts[pathParts.length - 1]
      
      // Method 3: From hash
      const idFromHash = window.location.hash.replace('#', '')
      
      // Use the first valid ID found
      const validId = idFromQuery || idFromPath || idFromHash
      
      if (validId && validId !== 'undefined' && validId !== 'null' && validId !== 'chat') {
        console.log('✅ Connection ID found:', validId)
        setConnectionId(validId)
      } else {
        console.error('❌ No valid connection ID found')
        setError('No valid connection ID provided. Please select a connection from the mentorship page.')
        setLoading(false)
      }
    }
  }, [])

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated && connectionId && connectionId !== 'undefined' && connectionId !== 'null') {
      setLoading(true)
      setError(null)
      fetchConnection()
      fetchMessages()
    }
  }, [isAuthenticated, connectionId])

  const fetchConnection = async () => {
    try {
      const useSupabase = (process.env.NEXT_PUBLIC_USE_SUPABASE_MENTORSHIP || 'false') === 'true'
      if (useSupabase) {
        const idNum = Number(connectionId)
        const { data: conn, error } = await supabase
          .from('mentorship_connections')
          .select('*')
          .eq('id', idNum)
          .single()
        if (error) throw error

        // Fetch profiles for mentor and mentee
        const { data: profs, error: perr } = await supabase
          .from('profiles')
          .select('id,username,full_name,email,role')
          .in('id', [conn.mentor_id, conn.mentee_id])
        if (perr) throw perr
        const idToProfile: Record<string, any> = {}
        ;(profs || []).forEach((p: any) => { idToProfile[p.id] = p })

        const transformed = {
          id: conn.id,
          mentor_id: conn.mentor_id,
          mentee_id: conn.mentee_id,
          status: conn.status,
          connection_message: conn.connection_message,
          goals: conn.goals || [],
          target_band_score: conn.target_band_score || 0,
          focus_areas: conn.focus_areas || [],
          mentor: idToProfile[conn.mentor_id] || null,
          mentee: idToProfile[conn.mentee_id] || null,
          created_at: conn.created_at,
        } as any
        setConnection(transformed)
        setRetryCount(0)
      } else {
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
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
          if (retryCount < maxRetries) {
            setRetryCount(prev => prev + 1)
            setTimeout(() => fetchConnection(), 2000)
            return
          }
          setError(`Failed to load connection details: ${errorData.detail}`)
        }
      }
    } catch (error) {
      console.error('❌ Error fetching connection:', error)
      
      // Retry logic for network errors
      if (retryCount < maxRetries) {
        console.log(`🔄 Retrying connection fetch due to network error (${retryCount + 1}/${maxRetries})`)
        setRetryCount(prev => prev + 1)
        setTimeout(() => fetchConnection(), 2000)
        return
      }
      
      setError('Failed to load connection details: Network error or server unreachable.')
    } finally {
      setLoading(false)
    }
  }

  const fetchMessages = async () => {
    try {
      const useSupabase = (process.env.NEXT_PUBLIC_USE_SUPABASE_MENTORSHIP || 'false') === 'true'
      if (useSupabase) {
        const idNum = Number(connectionId)
        const { data: msgs, error } = await supabase
          .from('mentorship_messages')
          .select('*')
          .eq('connection_id', idNum)
          .order('created_at', { ascending: true })
        if (error) throw error
        setMessages((msgs as any) || [])
        return
      }

      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found. Please log in again.')
        setLoading(false)
        return
      }
      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        setError(`Failed to load messages: ${errorData.detail}`)
      }
    } catch (error) {
      console.error('❌ Error fetching messages:', error)
      setError('Failed to load messages: Network error or server unreachable.')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    setSending(true)
    try {
      const useSupabase = (process.env.NEXT_PUBLIC_USE_SUPABASE_MENTORSHIP || 'false') === 'true'
      if (useSupabase) {
        const { data: sess } = await supabase.auth.getSession()
        const uid = sess?.session?.user?.id
        if (!uid) {
          setError('Please sign in again.')
          setSending(false)
          return
        }
        const idNum = Number(connectionId)
        const { data, error } = await supabase
          .from('mentorship_messages')
          .insert({
            connection_id: idNum,
            sender_id: uid,
            message_type: 'text',
            content: newMessage,
          })
          .select('*')
          .single()
        if (error) throw error
        setMessages(prev => [...prev, data as any])
        setNewMessage('')
        return
      }

      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found. Please log in again.')
        setSending(false)
        return
      }
      const formData = new FormData()
      formData.append('content', newMessage)
      formData.append('message_type', 'text')
      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/messages`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      if (response.ok) {
        const data = await response.json()
        if (data.data) {
          setMessages(prev => [...prev, data.data])
        }
        setNewMessage('')
      } else {
        const errorData = await response.json()
        setError(`Failed to send message: ${errorData.detail}`)
      }
    } catch (error) {
      console.error('❌ Error sending message:', error)
      setError('Failed to send message: Network error or server unreachable.')
    } finally {
      setSending(false)
    }
  }

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch (error) {
      return 'Invalid time'
    }
  }

  const handleRetry = () => {
    setError(null)
    setRetryCount(0)
    setLoading(true)
    fetchConnection()
    fetchMessages()
  }

  // Debug logging
  console.log('ChatPage render:', { 
    connectionId, 
    isAuthenticated, 
    user: user?.email, 
    loading, 
    error,
    retryCount 
  })

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Authenticating...</p>
        </div>
      </div>
    )
  }

  if (!connectionId || connectionId === 'undefined' || connectionId === 'null') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Invalid Connection</h3>
          <p className="text-red-600 mb-4">No valid connection ID provided.</p>
          <p className="text-sm text-gray-500 mb-4">
            URL: {typeof window !== 'undefined' ? window.location.pathname : 'N/A'}
          </p>
          <button
            onClick={() => router.push('/mentorship')}
            className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Back to Mentorship
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chat...</p>
          <p className="text-sm text-gray-500 mt-2">Connection ID: {connectionId}</p>
          {retryCount > 0 && (
            <p className="text-sm text-yellow-600 mt-2">Retrying... ({retryCount}/{maxRetries})</p>
          )}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Chat</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500 mb-4">Connection ID: {connectionId}</p>
          <div className="space-y-2">
            <button
              onClick={handleRetry}
              className="w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              Retry ({retryCount}/{maxRetries})
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/mentorship')}
                className="p-2 hover:bg-gray-100 rounded-full text-blue-600 hover:text-blue-800"
              >
                ← Back
              </button>
              
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Chat with {user?.id === connection.mentor_id 
                    ? connection.mentee?.full_name || 'Student'
                    : connection.mentor?.full_name || 'Mentor'
                  }
                </h1>
                <p className="text-sm text-gray-500">
                  Status: {connection.status} | ID: {connectionId}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow border overflow-hidden">
          {/* Messages Area */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Start the conversation</h3>
                <p className="text-gray-500">Send your first message to begin your mentorship journey.</p>
              </div>
            ) : (
              messages.map((message, index) => {
                const messageSenderId = Number(message.sender_id)
                const currentUserId = Number(user?.id)
                const isOwn = messageSenderId === currentUserId
                
                return (
                  <div key={message.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs px-4 py-2 rounded-lg ${
                      isOwn 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 text-gray-900'
                    }`}>
                      <p>{message.content}</p>
                      <div className={`text-xs mt-1 ${
                        isOwn ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.created_at)}
                      </div>
                    </div>
                  </div>
                )
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="border-t p-4">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
            
            <div className="flex space-x-3">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              <button
                onClick={() => sendMessage()}
                disabled={!newMessage.trim() || sending}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                {sending ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}