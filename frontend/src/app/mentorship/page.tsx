'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  CalendarDaysIcon,
  StarIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  AcademicCapIcon,
  TrophyIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  HeartIcon,
  SparklesIcon,
  PaperAirplaneIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface Mentor {
  id: number
  username: string
  full_name: string
  email: string
  role: string
  target_band_score: number
  current_level: string
  profile: {
    bio: string
    teaching_experience: string
    specializations: string[]
    average_rating: number
    total_mentees_helped: number
    is_available_for_mentorship: boolean
  }
}

interface Connection {
  id: number
  mentor_id: number
  mentee_id: number
  status: string
  connection_message: string
  goals: string[]
  target_band_score: number
  focus_areas: string[]
  created_at: string
  mentor_rating?: number
  mentee_rating?: number
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
}

interface Message {
  id: number
  connection_id: number
  sender_id: number
  message_type: string
  content: string
  created_at: string
}

interface Session {
  id: number
  connection_id: number
  title: string
  description?: string
  scheduled_at: string
  duration_minutes: number
  status: string
}

export default function MentorshipPage() {
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const router = useRouter()
  
  // State management
  const [activeTab, setActiveTab] = useState<'find' | 'connections' | 'sessions' | 'profile'>('find')
  
  // Modal state cleanup when switching tabs
  const handleTabChange = (tab: 'find' | 'connections' | 'sessions' | 'profile') => {
    // Close tab-specific modals when switching tabs (keep global modals open)
    setShowRatingModal(false)
    setShowWorkShareModal(false)
    setSelectedConnectionForRating(null)
    setSelectedConnectionForWorkShare(null)
    setActiveTab(tab)
  }
  const [mentors, setMentors] = useState<Mentor[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<{[key: string]: boolean}>({})
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Search filters
  const [searchFilters, setSearchFilters] = useState({
    specializations: '',
    target_band_score: '',
    timezone: ''
  })
  
  // Connection request form
  const [requestMessage, setRequestMessage] = useState('')
  const [requestGoals, setRequestGoals] = useState('')
  const [requestTargetBandScore, setRequestTargetBandScore] = useState('')
  const [requestFocusAreas, setRequestFocusAreas] = useState('')
  
  // Mentor profile form
  const [profileForm, setProfileForm] = useState({
    bio: '',
    teaching_experience: '',
    specializations: '',
    certifications: '',
    timezone: '',
    available_days: '',
    available_hours: '',
    is_available_for_mentorship: false,
    max_mentees: 3
  })
  
  // Messages
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessageContent, setNewMessageContent] = useState('')
  
  // Sessions
  const [sessions, setSessions] = useState<Session[]>([])
  const [newSessionTitle, setNewSessionTitle] = useState('')
  const [newSessionScheduledAt, setNewSessionScheduledAt] = useState('')
  const [newSessionDuration, setNewSessionDuration] = useState(60)
  
  // Session management
  const [showCreateSession, setShowCreateSession] = useState(false)
  const [selectedConnectionForSession, setSelectedConnectionForSession] = useState<Connection | null>(null)
  const [sessionForm, setSessionForm] = useState({
    title: '',
    description: '',
    session_type: 'general',
    scheduled_at: '',
    duration_minutes: 60,
    agenda: ''
  })
  
  // Rating system
  const [showRatingModal, setShowRatingModal] = useState(false)
  const [selectedConnectionForRating, setSelectedConnectionForRating] = useState<Connection | null>(null)
  const [ratingForm, setRatingForm] = useState({
    rating: 5,
    feedback: ''
  })
  
  // Work sharing system
  const [showWorkShareModal, setShowWorkShareModal] = useState(false)
  const [selectedConnectionForWorkShare, setSelectedConnectionForWorkShare] = useState<Connection | null>(null)
  const [workShareForm, setWorkShareForm] = useState({
    title: '',
    content: '',
    work_type: 'essay',
    description: ''
  })
  
  // Progress tracking
  const [progressStats, setProgressStats] = useState({
    totalSessions: 0,
    completedSessions: 0,
    totalConnections: 0,
    averageRating: 0,
    goalsAchieved: 0,
    totalGoals: 0
  })

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  // Set default tab and fetch data
  useEffect(() => {
    if (isAuthenticated && user) {
      // Set default tab based on user role
      if (user.role === 'mentor' || user.role === 'tutor') {
        setActiveTab('profile') // Start with profile setup for mentors
      } else {
        setActiveTab('find')
      }
      
      // Fetch data in parallel
      const fetchData = async () => {
        setLoading(true)
        try {
          await Promise.all([fetchMentors(), fetchConnections(), fetchSessions()])
        } catch (error) {
          console.error('Error fetching data:', error)
        } finally {
          setLoading(false)
        }
      }
      
      fetchData()
    }
  }, [isAuthenticated, user])

  // Clear messages after 5 seconds
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess(null)
        setError(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [success, error])

  // Calculate progress stats when sessions or connections change
  useEffect(() => {
    calculateProgressStats()
  }, [sessions, connections])

  const showMessage = (message: string, type: 'success' | 'error') => {
    if (type === 'success') {
      setSuccess(message)
      setError(null)
    } else {
      setError(message)
      setSuccess(null)
    }
  }

  const setActionLoadingState = (key: string, loading: boolean) => {
    setActionLoading(prev => ({ ...prev, [key]: loading }))
  }

  const fetchMentors = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const queryParams = new URLSearchParams()
      if (searchFilters.specializations) {
        queryParams.append('specializations', JSON.stringify(searchFilters.specializations.split(',').map(s => s.trim())))
      }
      if (searchFilters.target_band_score) {
        queryParams.append('target_band_score', searchFilters.target_band_score)
      }
      if (searchFilters.timezone) {
        queryParams.append('timezone', searchFilters.timezone)
      }

      const response = await fetch(`/api/v1/mentorship/mentors?${queryParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setMentors(data.mentors || [])
      } else {
        const errorData = await response.json()
        showMessage(`Failed to fetch mentors: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error fetching mentors:', error)
      showMessage('Failed to fetch mentors. Please try again.', 'error')
    }
  }

  const fetchConnections = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setConnections(data.connections || [])
      } else {
        const errorData = await response.json()
        showMessage(`Failed to fetch connections: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error fetching connections:', error)
      showMessage('Failed to fetch connections. Please try again.', 'error')
    }
  }

  const handleConnect = async (mentorId: number) => {
    const actionKey = `connect_${mentorId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Bearer ${token}`
        },
        body: new URLSearchParams({
          mentor_id: mentorId.toString(),
          message: requestMessage || 'Hi! I would like to connect with you for IELTS preparation.',
          goals: JSON.stringify(requestGoals ? requestGoals.split(',').map(s => s.trim()) : ['Improve IELTS score', 'Get personalized feedback']),
          target_band_score: requestTargetBandScore || '7.5',
          focus_areas: JSON.stringify(requestFocusAreas ? requestFocusAreas.split(',').map(s => s.trim()) : ['Writing', 'Speaking'])
        })
      })

      if (response.ok) {
        showMessage('Connection request sent successfully!', 'success')
        fetchConnections() // Refresh connections
        // Clear form
        setRequestMessage('')
        setRequestGoals('')
        setRequestTargetBandScore('')
        setRequestFocusAreas('')
      } else {
        const errorData = await response.json()
        showMessage(`Failed to send request: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error sending connection request:', error)
      showMessage('An error occurred while sending the connection request.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  const handleSaveProfile = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Bearer ${token}`
        },
        body: new URLSearchParams({
          bio: profileForm.bio,
          teaching_experience: profileForm.teaching_experience,
          specializations: JSON.stringify(profileForm.specializations.split(',').map(s => s.trim())),
          certifications: JSON.stringify(profileForm.certifications.split(',').map(s => s.trim())),
          timezone: profileForm.timezone,
          available_days: JSON.stringify(profileForm.available_days.split(',').map(s => s.trim())),
          available_hours: JSON.stringify(profileForm.available_hours.split(',').map(s => s.trim())),
          is_available_for_mentorship: profileForm.is_available_for_mentorship.toString(),
          max_mentees: profileForm.max_mentees.toString()
        })
      })

      if (response.ok) {
        showMessage('Profile updated successfully!', 'success')
        fetchConnections() // Refresh data
      } else {
        const errorData = await response.json()
        showMessage(`Failed to update profile: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error updating profile:', error)
      showMessage('An error occurred while updating your profile.', 'error')
    }
  }

  const handleAcceptRequest = async (connectionId: number) => {
    const actionKey = `accept_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/accept`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        showMessage('Connection request accepted!', 'success')
        fetchConnections()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to accept request: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error accepting request:', error)
      showMessage('An error occurred while accepting the request.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  const handleRejectRequest = async (connectionId: number) => {
    const actionKey = `reject_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/reject`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        showMessage('Connection request rejected.', 'success')
        fetchConnections()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to reject request: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error rejecting request:', error)
      showMessage('An error occurred while rejecting the request.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  const handleDeleteConnection = async (connectionId: number) => {
    if (!confirm('Are you sure you want to delete this connection? This action cannot be undone and will delete all messages.')) {
      return
    }

    const actionKey = `delete_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        showMessage('Connection deleted successfully.', 'success')
        fetchConnections()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to delete connection: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error deleting connection:', error)
      showMessage('An error occurred while deleting the connection.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  const handleSearch = () => {
    setLoading(true)
    fetchMentors().finally(() => setLoading(false))
  }

  // Session Management Functions
  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/sessions/upcoming`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions || [])
      } else {
        const errorData = await response.json()
        showMessage(`Failed to fetch sessions: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error fetching sessions:', error)
      showMessage('Failed to fetch sessions. Please try again.', 'error')
    }
  }

  const handleCreateSession = async (connectionId: number) => {
    const actionKey = `create_session_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/sessions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          title: sessionForm.title,
          description: sessionForm.description || '',
          session_type: sessionForm.session_type,
          scheduled_at: sessionForm.scheduled_at,
          duration_minutes: sessionForm.duration_minutes.toString(),
          agenda: sessionForm.agenda || ''
        })
      })

      if (response.ok) {
        showMessage('Session created successfully!', 'success')
        setShowCreateSession(false)
        setSessionForm({
          title: '',
          description: '',
          session_type: 'general',
          scheduled_at: '',
          duration_minutes: 60,
          agenda: ''
        })
        fetchSessions()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to create session: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error creating session:', error)
      showMessage('An error occurred while creating the session.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  const handleCompleteSession = async (sessionId: number, notes: string, rating: number, homework: string) => {
    const actionKey = `complete_session_${sessionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/sessions/${sessionId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          notes: notes || '',
          rating: rating.toString(),
          homework: homework || ''
        })
      })

      if (response.ok) {
        showMessage('Session completed successfully!', 'success')
        fetchSessions()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to complete session: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error completing session:', error)
      showMessage('An error occurred while completing the session.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  // Rating System Functions
  const handleRateMentorship = async (connectionId: number) => {
    const actionKey = `rate_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/rate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          rating: ratingForm.rating.toString(),
          feedback: ratingForm.feedback || ''
        })
      })

      if (response.ok) {
        showMessage('Rating submitted successfully!', 'success')
        setShowRatingModal(false)
        setRatingForm({ rating: 5, feedback: '' })
        fetchConnections()
      } else {
        const errorData = await response.json()
        showMessage(`Failed to submit rating: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error submitting rating:', error)
      showMessage('An error occurred while submitting the rating.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  // Work Sharing Functions
  const handleShareWork = async (connectionId: number) => {
    const actionKey = `share_work_${connectionId}`
    setActionLoadingState(actionKey, true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`/api/v1/mentorship/connections/${connectionId}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          content: `📝 **${workShareForm.title}**\n\n**Type:** ${workShareForm.work_type}\n**Description:** ${workShareForm.description}\n\n**Content:**\n${workShareForm.content}`,
          message_type: 'work_share'
        })
      })

      if (response.ok) {
        showMessage('Work shared successfully!', 'success')
        setShowWorkShareModal(false)
        setWorkShareForm({ title: '', content: '', work_type: 'essay', description: '' })
      } else {
        const errorData = await response.json()
        showMessage(`Failed to share work: ${errorData.detail}`, 'error')
      }
    } catch (error) {
      console.error('Error sharing work:', error)
      showMessage('An error occurred while sharing the work.', 'error')
    } finally {
      setActionLoadingState(actionKey, false)
    }
  }

  // Progress Tracking Functions
  const calculateProgressStats = () => {
    const completedSessions = sessions.filter(s => s.status === 'completed').length
    const totalSessions = sessions.length
    const totalConnections = connections.length
    
    // Calculate average rating from connections
    const ratings = connections
      .filter(conn => conn.mentor_rating || conn.mentee_rating)
      .map(conn => conn.mentor_rating || conn.mentee_rating)
    const averageRating = ratings.length > 0 ? ratings.reduce((a, b) => a + b, 0) / ratings.length : 0
    
    // Calculate goals achieved (simplified - based on completed sessions)
    const goalsAchieved = Math.min(completedSessions, 5) // Assume 5 goals max
    const totalGoals = 5
    
    setProgressStats({
      totalSessions,
      completedSessions,
      totalConnections,
      averageRating: Math.round(averageRating * 10) / 10,
      goalsAchieved,
      totalGoals
    })
  }

  const getConnectionStatus = (mentorId: number) => {
    const connection = connections.find(conn => 
      conn.mentor_id === mentorId && conn.mentee_id === user?.id
    )
    return connection ? connection.status : null
  }

  const getConnectionButtonText = (mentorId: number) => {
    const status = getConnectionStatus(mentorId)
    switch (status) {
      case 'pending': return 'Request Sent'
      case 'active': return 'Connected'
      case 'cancelled': return 'Rejected'
      default: return 'Connect'
    }
  }

  const getConnectionButtonStyle = (mentorId: number) => {
    const status = getConnectionStatus(mentorId)
    const isLoading = actionLoading[`connect_${mentorId}`]
    
    if (isLoading) {
      return 'bg-gray-400 text-white px-4 py-2 rounded-lg cursor-not-allowed text-sm'
    }
    
    switch (status) {
      case 'pending': return 'bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-all duration-200 text-sm'
      case 'active': return 'bg-green-500 text-white px-4 py-2 rounded-lg cursor-default text-sm'
      case 'cancelled': return 'bg-red-500 text-white px-4 py-2 rounded-lg cursor-default text-sm'
      default: return 'bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 text-sm'
    }
  }

  const isConnectionDisabled = (mentorId: number) => {
    const status = getConnectionStatus(mentorId)
    return status === 'pending' || status === 'active' || status === 'cancelled' || actionLoading[`connect_${mentorId}`]
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading mentorship data...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return null
  }

  const isMentorOrTutor = user.role === 'mentor' || user.role === 'tutor'

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Mentorship Platform
              </h1>
              <p className="text-gray-600 mt-1">
                Connect with mentors and mentees to accelerate your IELTS journey
              </p>
            </div>
            <Link 
              href="/dashboard/home" 
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {(success || error) && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-4 flex items-center"
            >
              <CheckCircleIcon className="h-5 w-5 mr-2" />
              {success}
            </motion.div>
          )}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center"
            >
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
              {error}
            </motion.div>
          )}
        </div>
      )}

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb Navigation */}
        <div className="mb-6">
          <nav className="flex items-center space-x-2 text-sm text-gray-500">
            <Link href="/dashboard/home" className="hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
            <span className="text-gray-900 font-medium">Mentorship</span>
            {activeTab !== 'find' && (
              <>
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-900 font-medium">
                  {activeTab === 'connections' 
                    ? (isMentorOrTutor ? 'My Mentees' : 'My Connections')
                    : activeTab === 'sessions' 
                    ? 'Sessions' 
                    : 'Find Mentors'
                  }
                </span>
              </>
            )}
          </nav>
        </div>

        {/* Progress Overview */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Your Mentorship Progress</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Total Connections */}
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <UserGroupIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-600">Connections</p>
                    <p className="text-2xl font-bold text-gray-900">{progressStats.totalConnections}</p>
                  </div>
                </div>
              </div>

              {/* Sessions Completed */}
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CalendarDaysIcon className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-600">Sessions</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {progressStats.completedSessions}/{progressStats.totalSessions}
                    </p>
                  </div>
                </div>
              </div>

              {/* Average Rating */}
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <svg className="h-6 w-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {progressStats.averageRating > 0 ? progressStats.averageRating.toFixed(1) : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Goals Progress */}
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-600">Goals</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {progressStats.goalsAchieved}/{progressStats.totalGoals}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm font-medium text-gray-700">
                  {Math.round((progressStats.goalsAchieved / progressStats.totalGoals) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(progressStats.goalsAchieved / progressStats.totalGoals) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-sm border border-white/20 p-1">
            <nav className="flex space-x-1">
              {[
                // Show "Find Mentors" for students, "My Profile" for mentors
                ...(user?.role === 'student' ? [{ id: 'find', name: 'Find Mentors', icon: MagnifyingGlassIcon }] : []),
                ...(isMentorOrTutor ? [{ id: 'profile', name: 'My Profile', icon: AcademicCapIcon }] : []),
                { id: 'connections', name: isMentorOrTutor ? 'My Mentees' : 'My Connections', icon: UserGroupIcon },
                { id: 'sessions', name: 'Sessions', icon: CalendarDaysIcon }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id as any)}
                  className={`flex items-center py-3 px-4 rounded-md font-medium text-sm transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                  }`}
                >
                  <tab.icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Find Mentors Tab */}
        {activeTab === 'find' && (
          <>
            {isMentorOrTutor ? (
              <div className="text-center py-12">
                <AcademicCapIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">You're a Mentor!</h3>
                <p className="text-gray-600 mb-6">As a mentor, you can help students by connecting with them. Check your connections to see mentee requests.</p>
                <button
                  onClick={() => handleTabChange('connections')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                >
                  View My Mentees
                </button>
              </div>
            ) : (
              <div>
                {/* Search Filters */}
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 mb-8">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Find Your Perfect Mentor</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label htmlFor="specializations" className="block text-sm font-medium text-gray-700">Specializations</label>
                      <input
                        type="text"
                        id="specializations"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={searchFilters.specializations}
                        onChange={(e) => setSearchFilters({ ...searchFilters, specializations: e.target.value })}
                        placeholder="e.g., Writing Task 2, Speaking"
                      />
                    </div>
                    <div>
                      <label htmlFor="target_band_score" className="block text-sm font-medium text-gray-700">Target Band Score</label>
                      <input
                        type="number"
                        id="target_band_score"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={searchFilters.target_band_score}
                        onChange={(e) => setSearchFilters({ ...searchFilters, target_band_score: e.target.value })}
                        placeholder="e.g., 7.0"
                        step="0.5"
                      />
                    </div>
                    <div>
                      <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">Timezone</label>
                      <input
                        type="text"
                        id="timezone"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={searchFilters.timezone}
                        onChange={(e) => setSearchFilters({ ...searchFilters, timezone: e.target.value })}
                        placeholder="e.g., UTC+8"
                      />
                    </div>
                  </div>
                  <div className="mt-6 text-right">
                    <button
                      onClick={handleSearch}
                      disabled={loading}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Searching...
                        </>
                      ) : (
                        <>
                          <MagnifyingGlassIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                          Search Mentors
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Mentor List */}
                {mentors.length === 0 ? (
                  <div className="text-center py-12">
                    <UserGroupIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No mentors found</h3>
                    <p className="text-gray-600">Try adjusting your search filters or check back later.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {mentors.map((mentor, index) => (
                      <motion.div
                        key={mentor.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
                      >
                        <div className="flex items-center mb-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                            {mentor.full_name?.charAt(0) || mentor.username.charAt(0)}
                          </div>
                          <div className="ml-4">
                            <h3 className="text-lg font-medium text-gray-900">{mentor.full_name || mentor.username}</h3>
                            <p className="text-sm text-blue-600">{mentor.role.charAt(0).toUpperCase() + mentor.role.slice(1)}</p>
                          </div>
                        </div>

                        <p className="text-gray-700 text-sm mb-4">{mentor.profile?.bio || 'No bio available.'}</p>

                        <div className="mb-4">
                          <p className="text-sm font-medium text-gray-800 mb-2">Specializations:</p>
                          <div className="flex flex-wrap gap-2">
                            {mentor.profile?.specializations?.map((spec, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {spec}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-600">
                            <p>Target Score: {mentor.target_band_score || 'N/A'}</p>
                            <p>Level: {mentor.current_level || 'N/A'}</p>
                          </div>
                          <button 
                            onClick={() => handleConnect(mentor.id)}
                            disabled={isConnectionDisabled(mentor.id)}
                            className={getConnectionButtonStyle(mentor.id)}
                          >
                            {actionLoading[`connect_${mentor.id}`] ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Sending...
                              </>
                            ) : (
                              getConnectionButtonText(mentor.id)
                            )}
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Connections Tab */}
        {activeTab === 'profile' && (
          <div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Mentor Profile Setup</h2>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${profileForm.is_available_for_mentorship ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className="text-sm text-gray-600">
                    {profileForm.is_available_for_mentorship ? 'Available for Mentorship' : 'Not Available'}
                  </span>
                </div>
              </div>
              
              <div className="space-y-6">
                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                  <textarea
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm({...profileForm, bio: e.target.value})}
                    placeholder="Tell students about yourself, your teaching experience, and what makes you a great mentor..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                  />
                </div>

                {/* Teaching Experience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Teaching Experience</label>
                  <textarea
                    value={profileForm.teaching_experience}
                    onChange={(e) => setProfileForm({...profileForm, teaching_experience: e.target.value})}
                    placeholder="Describe your teaching background, IELTS experience, and qualifications..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                  />
                </div>

                {/* Specializations */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Specializations</label>
                  <input
                    type="text"
                    value={profileForm.specializations}
                    onChange={(e) => setProfileForm({...profileForm, specializations: e.target.value})}
                    placeholder="Writing, Speaking, Listening, Reading (comma-separated)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Certifications */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Certifications</label>
                  <input
                    type="text"
                    value={profileForm.certifications}
                    onChange={(e) => setProfileForm({...profileForm, certifications: e.target.value})}
                    placeholder="IELTS Teacher Training, TESOL, etc. (comma-separated)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Availability Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Available Days</label>
                    <input
                      type="text"
                      value={profileForm.available_days}
                      onChange={(e) => setProfileForm({...profileForm, available_days: e.target.value})}
                      placeholder="Monday, Tuesday, Wednesday (comma-separated)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Available Hours</label>
                    <input
                      type="text"
                      value={profileForm.available_hours}
                      onChange={(e) => setProfileForm({...profileForm, available_hours: e.target.value})}
                      placeholder="Morning, Afternoon, Evening (comma-separated)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Max Mentees</label>
                    <input
                      type="number"
                      value={profileForm.max_mentees}
                      onChange={(e) => setProfileForm({...profileForm, max_mentees: parseInt(e.target.value)})}
                      min="1"
                      max="10"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                    <input
                      type="text"
                      value={profileForm.timezone}
                      onChange={(e) => setProfileForm({...profileForm, timezone: e.target.value})}
                      placeholder="UTC+5:30, EST, PST, etc."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Availability Toggle */}
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="available"
                    checked={profileForm.is_available_for_mentorship}
                    onChange={(e) => setProfileForm({...profileForm, is_available_for_mentorship: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="available" className="text-sm font-medium text-gray-700">
                    Available for Mentorship
                  </label>
                </div>

                {/* Save Button */}
                <div className="flex justify-end">
                  <button
                    onClick={handleSaveProfile}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    Save Profile
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'connections' && (
          <div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">My Mentorship Connections</h2>
                {user?.role === 'student' && (
                  <button
                    onClick={() => handleTabChange('find')}
                    className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                    Find More Mentors
                  </button>
                )}
              </div>
              
              {connections.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No connections yet</h3>
                  <p className="text-gray-600 mb-4">
                    {isMentorOrTutor 
                      ? "You don't have any mentees yet. Students will send you connection requests."
                      : "Start by finding a mentor to connect with and accelerate your IELTS journey."
                    }
                  </p>
                  {!isMentorOrTutor && (
                    <button
                      onClick={() => handleTabChange('find')}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      <MagnifyingGlassIcon className="h-4 w-4 mr-2 inline" />
                      Find Mentors
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {connections.map((connection, index) => (
                    <motion.div
                      key={connection.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            {isMentorOrTutor 
                              ? (connection.mentee?.full_name || connection.mentee?.username || 'M').charAt(0)
                              : (connection.mentor?.full_name || connection.mentor?.username || 'M').charAt(0)
                            }
                          </div>
                          <div className="ml-4">
                            <h3 className="font-semibold text-gray-900">
                              {isMentorOrTutor 
                                ? (connection.mentee?.full_name || connection.mentee?.username || 'Unknown User')
                                : (connection.mentor?.full_name || connection.mentor?.username || 'Unknown User')
                              }
                            </h3>
                            <p className="text-sm text-gray-600">
                              {connection.connection_message || 'No message provided'}
                            </p>
                            <div className="flex items-center mt-1">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                connection.status === 'active' ? 'bg-green-100 text-green-800' :
                                connection.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {connection.status.charAt(0).toUpperCase() + connection.status.slice(1)}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="flex space-x-2">
                          {connection.status === 'pending' && connection.mentor_id === user?.id && (
                            <>
                              <button
                                onClick={() => handleAcceptRequest(connection.id)}
                                disabled={actionLoading[`accept_${connection.id}`]}
                                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                {actionLoading[`accept_${connection.id}`] ? (
                                  <>
                                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                    Accepting...
                                  </>
                                ) : (
                                  <>
                                    <CheckCircleIcon className="h-3 w-3 mr-1" />
                                    Accept
                                  </>
                                )}
                              </button>
                              <button
                                onClick={() => handleRejectRequest(connection.id)}
                                disabled={actionLoading[`reject_${connection.id}`]}
                                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                {actionLoading[`reject_${connection.id}`] ? (
                                  <>
                                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                    Rejecting...
                                  </>
                                ) : (
                                  <>
                                    <XCircleIcon className="h-3 w-3 mr-1" />
                                    Reject
                                  </>
                                )}
                              </button>
                            </>
                          )}
                          <div className="flex space-x-2">
                            {connection.status === 'active' && (
                              <>
                                <button
                                  onClick={() => {
                                    console.log('Navigating to chat for connection:', connection.id)
                                    router.push(`/mentorship/chat/${connection.id}`)
                                  }}
                                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                                >
                                  <ChatBubbleLeftRightIcon className="h-3 w-3 mr-1" />
                                  Message
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedConnectionForSession(connection)
                                    setShowCreateSession(true)
                                  }}
                                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
                                >
                                  <CalendarDaysIcon className="h-3 w-3 mr-1" />
                                  Schedule
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedConnectionForRating(connection)
                                    setShowRatingModal(true)
                                  }}
                                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 transition-colors"
                                >
                                  <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                  </svg>
                                  Rate
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedConnectionForWorkShare(connection)
                                    setShowWorkShareModal(true)
                                  }}
                                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
                                >
                                  <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                  Share Work
                                </button>
                              </>
                            )}
                            <button
                              onClick={() => handleDeleteConnection(connection.id)}
                              disabled={actionLoading[`delete_${connection.id}`]}
                              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {actionLoading[`delete_${connection.id}`] ? (
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                              ) : (
                                <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              )}
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Rating Modal - Inside Connections Tab */}
            {showRatingModal && selectedConnectionForRating && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Rate Your Mentorship Experience</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Rating</label>
                      <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            onClick={() => setRatingForm({...ratingForm, rating: star})}
                            className={`text-2xl ${
                              star <= ratingForm.rating 
                                ? 'text-yellow-400' 
                                : 'text-gray-300 hover:text-yellow-300'
                            } transition-colors`}
                          >
                            ★
                          </button>
                        ))}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {ratingForm.rating === 1 && 'Poor'}
                        {ratingForm.rating === 2 && 'Fair'}
                        {ratingForm.rating === 3 && 'Good'}
                        {ratingForm.rating === 4 && 'Very Good'}
                        {ratingForm.rating === 5 && 'Excellent'}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Feedback (Optional)</label>
                      <textarea
                        value={ratingForm.feedback}
                        onChange={(e) => setRatingForm({...ratingForm, feedback: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={4}
                        placeholder="Share your experience with this mentor..."
                      />
                    </div>
                  </div>
                  
                  <div className="flex space-x-3 mt-6">
                    <button
                      onClick={() => setShowRatingModal(false)}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleRateMentorship(selectedConnectionForRating.id)}
                      disabled={actionLoading[`rate_${selectedConnectionForRating.id}`]}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-lg hover:from-yellow-700 hover:to-orange-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {actionLoading[`rate_${selectedConnectionForRating.id}`] ? 'Submitting...' : 'Submit Rating'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Work Sharing Modal - Inside Connections Tab */}
            {showWorkShareModal && selectedConnectionForWorkShare && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-2xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Share Your Work</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Work Title</label>
                      <input
                        type="text"
                        value={workShareForm.title}
                        onChange={(e) => setWorkShareForm({...workShareForm, title: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., IELTS Writing Task 2 Essay"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Work Type</label>
                      <select
                        value={workShareForm.work_type}
                        onChange={(e) => setWorkShareForm({...workShareForm, work_type: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="essay">Essay</option>
                        <option value="speaking_practice">Speaking Practice</option>
                        <option value="reading_exercise">Reading Exercise</option>
                        <option value="listening_practice">Listening Practice</option>
                        <option value="homework">Homework</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={workShareForm.description}
                        onChange={(e) => setWorkShareForm({...workShareForm, description: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                        placeholder="Brief description of your work and what feedback you're looking for..."
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Work Content</label>
                      <textarea
                        value={workShareForm.content}
                        onChange={(e) => setWorkShareForm({...workShareForm, content: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={10}
                        placeholder="Paste your essay, speaking script, or other work content here..."
                      />
                    </div>
                  </div>
                  
                  <div className="flex space-x-3 mt-6">
                    <button
                      onClick={() => setShowWorkShareModal(false)}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleShareWork(selectedConnectionForWorkShare.id)}
                      disabled={!workShareForm.title || !workShareForm.content || actionLoading[`share_work_${selectedConnectionForWorkShare.id}`]}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {actionLoading[`share_work_${selectedConnectionForWorkShare.id}`] ? 'Sharing...' : 'Share Work'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="space-y-6">
            {/* Session Management Header */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Session Management</h2>
                <button
                  onClick={() => handleTabChange('connections')}
                  className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <UserGroupIcon className="h-4 w-4 mr-2" />
                  Manage Connections
                </button>
              </div>
              
              {sessions.length === 0 ? (
                <div className="text-center py-12">
                  <CalendarDaysIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No sessions scheduled</h3>
                  <p className="text-gray-600 mb-4">Connect with a mentor to schedule your first session.</p>
                  <button
                    onClick={() => handleTabChange('connections')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <UserGroupIcon className="h-4 w-4 mr-2 inline" />
                    View Connections
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {sessions.map((session, index) => (
                    <motion.div
                      key={session.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200 hover:shadow-lg transition-all duration-300"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <CalendarDaysIcon className="h-5 w-5 text-blue-600 mr-2" />
                            <h3 className="text-lg font-semibold text-gray-900">{session.title}</h3>
                            <span className={`ml-3 px-2 py-1 rounded-full text-xs font-medium ${
                              session.status === 'scheduled' ? 'bg-green-100 text-green-800' :
                              session.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                              session.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {session.status.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div className="flex items-center">
                              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              {new Date(session.scheduled_at).toLocaleDateString()}
                            </div>
                            <div className="flex items-center">
                              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {new Date(session.scheduled_at).toLocaleTimeString()}
                            </div>
                            <div className="flex items-center">
                              <svg className="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {session.duration_minutes} minutes
                            </div>
                          </div>
                          
                          {session.description && (
                            <p className="mt-3 text-gray-700">{session.description}</p>
                          )}
                        </div>
                        
                        <div className="flex space-x-2 ml-4">
                          {session.status === 'scheduled' && (
                            <button
                              onClick={() => {
                                if (confirm('Mark this session as completed?')) {
                                  handleCompleteSession(session.id, 'Session completed', 5, '')
                                }
                              }}
                              className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                            >
                              Complete
                            </button>
                          )}
                          <button
                            onClick={() => {
                              // TODO: Add session details modal
                              alert('Session details feature coming soon!')
                            }}
                            className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                          >
                            Details
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}

        {/* Create Session Modal - Global (accessible from any tab) */}
        {showCreateSession && selectedConnectionForSession && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Schedule New Session</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Session Title</label>
                  <input
                    type="text"
                    value={sessionForm.title}
                    onChange={(e) => setSessionForm({...sessionForm, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Writing Practice Session"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={sessionForm.description}
                    onChange={(e) => setSessionForm({...sessionForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Session description and objectives..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Session Type</label>
                  <select
                    value={sessionForm.session_type}
                    onChange={(e) => setSessionForm({...sessionForm, session_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="general">General Discussion</option>
                    <option value="writing_feedback">Writing Feedback</option>
                    <option value="speaking_practice">Speaking Practice</option>
                    <option value="reading_comprehension">Reading Comprehension</option>
                    <option value="listening_practice">Listening Practice</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time</label>
                  <input
                    type="datetime-local"
                    value={sessionForm.scheduled_at}
                    onChange={(e) => setSessionForm({...sessionForm, scheduled_at: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    value={sessionForm.duration_minutes}
                    onChange={(e) => setSessionForm({...sessionForm, duration_minutes: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="15"
                    max="180"
                    step="15"
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateSession(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleCreateSession(selectedConnectionForSession.id)}
                  disabled={!sessionForm.title || !sessionForm.scheduled_at || actionLoading[`create_session_${selectedConnectionForSession.id}`]}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {actionLoading[`create_session_${selectedConnectionForSession.id}`] ? 'Creating...' : 'Create Session'}
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
