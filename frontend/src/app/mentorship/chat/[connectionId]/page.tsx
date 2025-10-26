'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter, useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon,
  PaperAirplaneIcon,
  PaperClipIcon,
  PhotoIcon,
  DocumentTextIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  EllipsisVerticalIcon,
  UserCircleIcon,
  ClockIcon,
  CheckIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

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
  const connectionId = params.connectionId as string
  
  // Force browser to recognize new styles
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      .message-bubble {
        background-color: #f3f4f6 !important;
        color: #000000 !important;
        border-radius: 16px !important;
        padding: 8px 16px !important;
        margin: 4px 0 !important;
        display: block !important;
        min-height: 40px !important;
        width: fit-content !important;
        max-width: 80% !important;
      }
      .message-text {
        color: #000000 !important;
        font-size: 14px !important;
        font-weight: normal !important;
        text-shadow: none !important;
        white-space: pre-wrap !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
      }
    `
    document.head.appendChild(style)
    return () => {
      document.head.removeChild(style)
    }
  }, [])
  
  const [connection, setConnection] = useState<Connection | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    if (isAuthenticated && connectionId) {
      setLoading(true)
      fetchConnection()
      fetchMessages()
    }
  }, [isAuthenticated, connectionId])

  const fetchConnection = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found')
        setLoading(false)
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setConnection(data.connection)
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        setError(`Failed to load connection details: ${errorData.detail}`)
      }
    } catch (error) {
      console.error('Error fetching connection:', error)
      setError('Failed to load connection details')
    } finally {
      setLoading(false)
    }
  }

  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('No authentication token found')
        setLoading(false)
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}/messages`, {
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
      console.error('Error fetching messages:', error)
      setError('Failed to load messages')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (messageType: 'text' | 'file' = 'text', file?: File) => {
    if (!newMessage.trim() && !file) return

    setSending(true)
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const formData = new FormData()
      formData.append('content', newMessage || '')
      formData.append('message_type', messageType)
      
      if (file) {
        formData.append('file', file)
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}/messages`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Send message response:', data)
        // The API returns data.data, not data.message
        if (data.data) {
          console.log('Adding message to state:', data.data)
          setMessages(prev => {
            const newMessages = [...prev, data.data]
            console.log('Updated messages array:', newMessages)
            return newMessages
          })
        } else {
          console.error('No data.data in response:', data)
        }
        setNewMessage('')
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } else {
        const errorData = await response.json()
        setError(`Failed to send message: ${errorData.detail}`)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setError('Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      sendMessage('file', file)
    }
  }

  const getOtherUser = () => {
    if (!connection || !user) return null
    return user.id === connection.mentor_id ? connection.mentee : connection.mentor
  }

  const formatTime = (timestamp: string) => {
    try {
      if (!timestamp) {
        console.log('formatTime: No timestamp provided')
        return 'No time'
      }
      
      console.log('formatTime: Processing timestamp:', timestamp)
      // Simple and direct approach
      const date = new Date(timestamp)
      console.log('formatTime: Parsed date:', date)
      
      if (isNaN(date.getTime())) {
        console.log('formatTime: Invalid date')
        return 'Invalid time'
      }
      
      const result = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      console.log('formatTime: Result:', result)
      return result
    } catch (error) {
      console.log('formatTime: Error:', error)
      return 'Invalid time'
    }
  }

  const formatDate = (timestamp: string) => {
    try {
      if (!timestamp) {
        console.log('formatDate: No timestamp provided')
        return 'No date'
      }
      
      console.log('formatDate: Processing timestamp:', timestamp)
      // Simple and direct approach
      const date = new Date(timestamp)
      console.log('formatDate: Parsed date:', date)
      
      if (isNaN(date.getTime())) {
        console.log('formatDate: Invalid date')
        return 'Invalid date'
      }
      
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      
      let result
      if (date.toDateString() === today.toDateString()) {
        result = 'Today'
      } else if (date.toDateString() === yesterday.toDateString()) {
        result = 'Yesterday'
      } else {
        result = date.toLocaleDateString()
      }
      
      console.log('formatDate: Result:', result)
      return result
    } catch (error) {
      console.log('formatDate: Error:', error)
      return 'Invalid date'
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Authenticating...</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chat...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Chat</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <div className="space-y-2">
              <button
                onClick={() => {
                  setError(null)
                  setLoading(true)
                  fetchConnection()
                  fetchMessages()
                }}
                className="w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Retry
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
      </div>
    )
  }

  if (!isAuthenticated || !user || !connection) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Chat Not Found</h2>
          <p className="text-gray-600 mb-6">This chat connection could not be found or you don't have access to it.</p>
          <button
            onClick={() => router.push('/mentorship')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Mentorship
          </button>
        </div>
      </div>
    )
  }

  const otherUser = getOtherUser()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/mentorship')}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                  {otherUser?.full_name?.charAt(0) || otherUser?.username?.charAt(0) || 'U'}
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">
                    {otherUser?.full_name || otherUser?.username || 'Unknown User'}
                  </h1>
                  <p className="text-sm text-gray-500">
                    {otherUser?.role === 'mentor' ? 'Mentor' : 'Mentee'} • {connection.status}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <VideoCameraIcon className="h-5 w-5 text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <EllipsisVerticalIcon className="h-5 w-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border h-[600px] flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <UserCircleIcon className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Start the conversation</h3>
                <p className="text-gray-600">Send your first message to begin your mentorship journey!</p>
              </div>
            ) : (
              messages.map((message, index) => {
                // Try multiple ways to get the current user ID
                const messageSenderId = Number(message.sender_id)
                const currentUserIdFromId = Number(user?.id)
                const currentUserIdFromUserId = Number(user?.user_id)
                const currentUserIdFromSub = Number(user?.sub)
                
                // Try all possible user ID fields
                const isOwn = messageSenderId === currentUserIdFromId || 
                             messageSenderId === currentUserIdFromUserId || 
                             messageSenderId === currentUserIdFromSub
                
                console.log('🔍 ALIGNMENT DEBUG:', {
                  messageSenderId: message.sender_id,
                  messageSenderIdType: typeof message.sender_id,
                  messageSenderIdNumber: messageSenderId,
                  currentUserId: user?.id,
                  currentUserIdType: typeof user?.id,
                  currentUserIdNumber: currentUserIdFromId,
                  currentUserIdFromUserId: currentUserIdFromUserId,
                  currentUserIdFromSub: currentUserIdFromSub,
                  isOwn: isOwn,
                  userObject: user,
                  userKeys: user ? Object.keys(user) : 'no user'
                })
                const showDate = index === 0 || 
                  formatDate(messages[index - 1].created_at) !== formatDate(message.created_at)
                
                // Debug logging for each message
                console.log(`Rendering message ${index}:`, {
                  id: message.id,
                  content: message.content,
                  sender_id: message.sender_id,
                  currentUserId: user.id,
                  isOwn: isOwn,
                  hasContent: !!message.content,
                  contentLength: message.content?.length || 0,
                  senderInfo: message.sender
                })

                return (
                  <div key={`${message.id}-${message.created_at}`}>
                    {showDate && (
                      <div className="text-center py-2">
                        <span style={{ 
                          backgroundColor: '#f3f4f6 !important', 
                          color: '#4b5563 !important',
                          fontSize: '14px !important',
                          padding: '4px 12px !important',
                          borderRadius: '9999px !important',
                          display: 'inline-block !important'
                        }}>
                          {formatDate(message.created_at)}
                        </span>
                      </div>
                    )}
                    
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md ${isOwn ? 'order-2' : 'order-1'}`}>
                        {!isOwn && (
                          <div className="flex items-center space-x-2 mb-1">
                            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                              {message.sender?.full_name?.charAt(0) || message.sender?.username?.charAt(0) || 'U'}
                            </div>
                            <span className="text-sm font-medium text-gray-900">
                              {message.sender?.full_name || message.sender?.username || 'Unknown'}
                            </span>
                          </div>
                        )}
                        
                        <div 
                          key={`bubble-${message.id}`}
                          className="message-bubble"
                          style={{
                            borderRadius: '16px !important',
                            padding: '8px 16px !important',
                            backgroundColor: isOwn ? '#3b82f6 !important' : '#f3f4f6 !important',
                            border: isOwn ? '2px solid #2563eb !important' : '1px solid #e5e7eb !important',
                            boxShadow: isOwn ? '0 1px 3px rgba(0,0,0,0.1) !important' : 'none !important',
                            margin: '4px 0 !important',
                            display: 'block !important',
                            minHeight: '40px !important',
                            width: 'fit-content !important',
                            maxWidth: '80% !important',
                            color: isOwn ? '#ffffff !important' : '#000000 !important',
                            position: 'relative'
                          }}>
                          
                          {/* Removed debug indicator that overlapped message content */}
                          
                          {message.message_type === 'text' ? (
                            <div>
                              <p 
                                key={`text-${message.id}`}
                                className="message-text"
                                style={{
                                  fontSize: '14px !important',
                                  color: isOwn ? '#ffffff !important' : '#000000 !important',
                                  fontWeight: 'normal !important',
                                  textShadow: 'none !important',
                                  whiteSpace: 'pre-wrap !important',
                                  margin: '0 !important',
                                  lineHeight: '1.4 !important',
                                  display: 'block !important',
                                   visibility: 'visible',
                                   opacity: 1
                                }}>{message.content || 'NO CONTENT'}</p>
                            </div>
                          ) : (
                            <div className="space-y-2">
                              <div className="flex items-center space-x-2">
                                {message.message_type === 'image' && <PhotoIcon className="h-4 w-4" style={{
                                  color: '#4b5563 !important'
                                }} />}
                                {message.message_type === 'file' && <DocumentTextIcon className="h-4 w-4" style={{
                                  color: '#4b5563 !important'
                                }} />}
                                {message.message_type === 'audio' && <MicrophoneIcon className="h-4 w-4" style={{
                                  color: '#4b5563 !important'
                                }} />}
                                {message.message_type === 'video' && <VideoCameraIcon className="h-4 w-4" style={{
                                  color: '#4b5563 !important'
                                }} />}
                                <span className="text-sm font-medium" style={{
                                  color: '#000000 !important'
                                }}>{message.file_name}</span>
                              </div>
                              {message.content && (
                                <p className="text-sm whitespace-pre-wrap" style={{
                                  color: '#000000 !important'
                                }}>{message.content}</p>
                              )}
                            </div>
                          )}
                        </div>
                        
                        <div className={`flex items-center space-x-1 mt-1 ${isOwn ? 'justify-end' : 'justify-start'}`}>
                          <span style={{ 
                            color: '#6b7280 !important',
                            fontSize: '12px !important',
                            display: 'inline-block !important'
                          }}>
                            {formatTime(message.created_at)}
                          </span>
                          {isOwn && (
                            <div className="flex items-center space-x-1">
                              {message.is_read ? (
                                <CheckCircleIcon className="h-3 w-3 text-blue-500" />
                              ) : (
                                <CheckIcon className="h-3 w-3 text-gray-400" />
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
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
            
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      sendMessage()
                    }
                  }}
                  placeholder="Type your message..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <PaperClipIcon className="h-5 w-5" />
                </button>
                
                <button
                  onClick={() => sendMessage()}
                  disabled={!newMessage.trim() || sending}
                  className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {sending ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <PaperAirplaneIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
