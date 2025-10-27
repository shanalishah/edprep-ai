'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter, useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
  PhotoIcon,
  PaperClipIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  StarIcon,
  ChatBubbleLeftIcon,
  ClockIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

interface WorkItem {
  id: number
  connection_id: number
  author_id: number
  title: string
  description: string
  work_type: 'essay' | 'practice_test' | 'speaking_recording' | 'reading_exercise' | 'other'
  content: string
  file_url?: string
  file_name?: string
  file_size?: number
  status: 'draft' | 'submitted' | 'reviewed' | 'approved'
  created_at: string
  updated_at: string
  author?: {
    id: number
    username: string
    full_name: string
    role: string
  }
  feedback?: {
    id: number
    reviewer_id: number
    rating: number
    comments: string
    suggestions: string[]
    created_at: string
    reviewer?: {
      id: number
      username: string
      full_name: string
      role: string
    }
  }
}

interface Connection {
  id: number
  mentor_id: number
  mentee_id: number
  status: 'pending' | 'active' | 'completed' | 'cancelled'
  mentor: {
    id: number
    username: string
    full_name: string
    role: string
  }
  mentee: {
    id: number
    username: string
    full_name: string
    role: string
  }
}

export default function WorkspacePage() {
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const connectionId = params.connectionId as string
  
  const [connection, setConnection] = useState<Connection | null>(null)
  const [workItems, setWorkItems] = useState<WorkItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedWork, setSelectedWork] = useState<WorkItem | null>(null)
  
  // Form states
  const [newWork, setNewWork] = useState({
    title: '',
    description: '',
    work_type: 'essay' as const,
    content: ''
  })
  const [submitting, setSubmitting] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated && connectionId) {
      fetchConnection()
      fetchWorkItems()
    }
  }, [isAuthenticated, connectionId])

  const fetchConnection = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setConnection(data.connection)
      } else {
        setError('Failed to load connection details')
      }
    } catch (error) {
      console.error('Error fetching connection:', error)
      setError('Failed to load connection details')
    }
  }

  const fetchWorkItems = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}/workspace`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setWorkItems(data.work_items || [])
      } else {
        setError('Failed to load work items')
      }
    } catch (error) {
      console.error('Error fetching work items:', error)
      setError('Failed to load work items')
    } finally {
      setLoading(false)
    }
  }

  const createWorkItem = async (file?: File) => {
    if (!newWork.title.trim() || !newWork.content.trim()) return

    setSubmitting(true)
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const formData = new FormData()
      formData.append('title', newWork.title)
      formData.append('description', newWork.description)
      formData.append('work_type', newWork.work_type)
      formData.append('content', newWork.content)
      
      if (file) {
        formData.append('file', file)
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/mentorship/connections/${connectionId}/workspace`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setWorkItems(prev => [data.work_item, ...prev])
        setNewWork({ title: '', description: '', work_type: 'essay', content: '' })
        setShowCreateForm(false)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } else {
        const errorData = await response.json()
        setError(`Failed to create work item: ${errorData.detail}`)
      }
    } catch (error) {
      console.error('Error creating work item:', error)
      setError('Failed to create work item')
    } finally {
      setSubmitting(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      createWorkItem(file)
    }
  }

  const getOtherUser = () => {
    if (!connection || !user) return null
    return user.id === connection.mentor_id ? connection.mentee : connection.mentor
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'submitted': return 'bg-yellow-100 text-yellow-800'
      case 'reviewed': return 'bg-blue-100 text-blue-800'
      case 'approved': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getWorkTypeIcon = (type: string) => {
    switch (type) {
      case 'essay': return <DocumentTextIcon className="h-5 w-5" />
      case 'practice_test': return <DocumentTextIcon className="h-5 w-5" />
      case 'speaking_recording': return <PhotoIcon className="h-5 w-5" />
      case 'reading_exercise': return <DocumentTextIcon className="h-5 w-5" />
      default: return <DocumentTextIcon className="h-5 w-5" />
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading workspace...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user || !connection) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Workspace Not Found</h2>
          <p className="text-gray-600 mb-6">This workspace could not be found or you don't have access to it.</p>
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
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/mentorship')}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                  <DocumentTextIcon className="h-5 w-5" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">Learning Workspace</h1>
                  <p className="text-sm text-gray-500">
                    Collaborate with {otherUser?.full_name || otherUser?.username || 'Unknown User'}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Share Work
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Work Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workItems.length === 0 ? (
            <div className="col-span-full text-center py-12 bg-white rounded-lg shadow-sm border">
              <DocumentTextIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No work shared yet</h3>
              <p className="text-gray-600 mb-6">Start by sharing your first essay, practice test, or learning material.</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Share Your First Work
              </button>
            </div>
          ) : (
            workItems.map((work, index) => (
              <motion.div
                key={work.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedWork(work)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white">
                        {getWorkTypeIcon(work.work_type)}
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 line-clamp-1">{work.title}</h3>
                        <p className="text-sm text-gray-500 capitalize">{work.work_type.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(work.status)}`}>
                      {work.status}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{work.description}</p>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <UserIcon className="h-4 w-4" />
                        <span>{work.author?.full_name || work.author?.username || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="h-4 w-4" />
                        <span>{new Date(work.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    {work.feedback && (
                      <div className="flex items-center space-x-1">
                        <StarIcon className="h-4 w-4 text-yellow-500" />
                        <span>{work.feedback.rating}/5</span>
                      </div>
                    )}
                  </div>

                  {work.feedback && (
                    <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-6 h-6 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                          {work.feedback.reviewer?.full_name?.charAt(0) || work.feedback.reviewer?.username?.charAt(0) || 'R'}
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {work.feedback.reviewer?.full_name || work.feedback.reviewer?.username || 'Reviewer'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(work.feedback.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">{work.feedback.comments}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Create Work Item Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Share Your Work</h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <XCircleIcon className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); createWorkItem(); }}>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                      Title *
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={newWork.title}
                      onChange={(e) => setNewWork({ ...newWork, title: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., IELTS Writing Task 2 - Technology Essay"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="work_type" className="block text-sm font-medium text-gray-700 mb-1">
                      Work Type *
                    </label>
                    <select
                      id="work_type"
                      value={newWork.work_type}
                      onChange={(e) => setNewWork({ ...newWork, work_type: e.target.value as any })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="essay">Essay</option>
                      <option value="practice_test">Practice Test</option>
                      <option value="speaking_recording">Speaking Recording</option>
                      <option value="reading_exercise">Reading Exercise</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      value={newWork.description}
                      onChange={(e) => setNewWork({ ...newWork, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={3}
                      placeholder="Brief description of your work..."
                    />
                  </div>

                  <div>
                    <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                      Content *
                    </label>
                    <textarea
                      id="content"
                      value={newWork.content}
                      onChange={(e) => setNewWork({ ...newWork, content: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={8}
                      placeholder="Paste your essay, practice test answers, or other content here..."
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-1">
                      Attach File (Optional)
                    </label>
                    <input
                      ref={fileInputRef}
                      type="file"
                      id="file"
                      onChange={handleFileUpload}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      accept=".pdf,.doc,.docx,.txt,.mp3,.mp4,.wav"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Supported formats: PDF, DOC, DOCX, TXT, MP3, MP4, WAV
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || !newWork.title.trim() || !newWork.content.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? 'Sharing...' : 'Share Work'}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}


