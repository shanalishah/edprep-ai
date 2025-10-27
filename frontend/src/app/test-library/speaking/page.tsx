'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon,
  ClockIcon,
  StarIcon,
  ChartBarIcon,
  PlayIcon,
  BookOpenIcon,
  AcademicCapIcon,
  TrophyIcon,
  ArrowLeftIcon,
  EyeIcon,
  SparklesIcon,
  MicrophoneIcon,
  CpuChipIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface SpeakingTest {
  id: string
  title: string
  type: 'Academic' | 'General Training'
  difficulty: 'Easy' | 'Medium' | 'Hard'
  estimated_time: string
  description: string
  topics: string[]
}

export default function SpeakingTestsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [tests, setTests] = useState<SpeakingTest[]>([])
  const [filter, setFilter] = useState<'all' | 'Academic' | 'General Training'>('all')
  const [difficulty, setDifficulty] = useState<'all' | 'Easy' | 'Medium' | 'Hard'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      loadSpeakingTests()
    }
  }, [isAuthenticated])

  const loadSpeakingTests = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/speaking`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const apiTests = await response.json()
        setTests(apiTests)
      } else {
        // Fallback to mock data if API fails
        const mockTests: SpeakingTest[] = [
          {
            id: "speaking_mock_1",
            title: "General Topics Speaking Test",
            type: "General Training",
            difficulty: "Easy",
            estimated_time: "11-14 minutes",
            description: "Practice speaking on familiar topics with AI examiner",
            topics: ["Personal Information", "Hobbies", "Travel", "Food", "Technology"]
          },
          {
            id: "speaking_mock_2",
            title: "Academic Discussion Test",
            type: "Academic",
            difficulty: "Medium",
            estimated_time: "11-14 minutes",
            description: "Advanced speaking practice with complex topics",
            topics: ["Education", "Environment", "Technology", "Society", "Culture"]
          },
          {
            id: "speaking_mock_3",
            title: "Professional Communication Test",
            type: "General Training",
            difficulty: "Hard",
            estimated_time: "11-14 minutes",
            description: "Business and professional speaking scenarios",
            topics: ["Work", "Leadership", "Communication", "Problem Solving", "Innovation"]
          }
        ]
        setTests(mockTests)
      }
    } catch (error) {
      console.error('Error loading speaking tests:', error)
      // Fallback to mock data
      const mockTests: SpeakingTest[] = [
        {
          id: "speaking_mock_1",
          title: "General Topics Speaking Test",
          type: "General Training",
          difficulty: "Easy",
          estimated_time: "11-14 minutes",
          description: "Practice speaking on familiar topics with AI examiner",
          topics: ["Personal Information", "Hobbies", "Travel", "Food", "Technology"]
        }
      ]
      setTests(mockTests)
    } finally {
      setLoading(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Academic': return 'bg-blue-100 text-blue-800'
      case 'General Training': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredTests = tests.filter(test => {
    const matchesFilter = filter === 'all' || test.type === filter
    const matchesDifficulty = difficulty === 'all' || test.difficulty === difficulty
    return matchesFilter && matchesDifficulty
  })

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <Link href="/test-library" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <ArrowLeftIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Speaking Tests</h1>
                <p className="text-gray-600">AI-Powered IELTS Speaking Practice</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <CpuChipIcon className="h-8 w-8 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">AI Examiner</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Tests</p>
                <p className="text-2xl font-bold text-gray-900">{tests.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <MicrophoneIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Examiner</p>
                <p className="text-2xl font-bold text-gray-900">Active</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ClockIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Test Duration</p>
                <p className="text-2xl font-bold text-gray-900">11-14 min</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <SparklesIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Features</p>
                <p className="text-2xl font-bold text-gray-900">Advanced</p>
              </div>
            </div>
          </div>
        </div>

        {/* AI Features Banner */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-6 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-2">🤖 AI-Powered Speaking Tests</h2>
              <p className="text-blue-100">
                Practice with our intelligent AI examiner that conducts realistic IELTS speaking tests, 
                provides instant feedback, and scores your performance across all criteria.
              </p>
            </div>
            <div className="hidden md:block">
              <CpuChipIcon className="h-16 w-16 text-blue-200" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Tests</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Test Type</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Types</option>
                <option value="Academic">Academic</option>
                <option value="General Training">General Training</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Levels</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Bot Test Card */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <ChatBubbleLeftRightIcon className="h-6 w-6 mr-2" />
                  <h3 className="text-xl font-bold">AI Speaking Test Bot</h3>
                </div>
                <p className="text-blue-100 mb-4">
                  Experience a realistic IELTS speaking test with our AI examiner bot. 
                  Have a natural voice-to-voice conversation and receive comprehensive feedback.
                </p>
                <div className="flex items-center space-x-4 text-sm text-blue-100">
                  <div className="flex items-center">
                    <MicrophoneIcon className="h-4 w-4 mr-1" />
                    Voice-to-voice conversation
                  </div>
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    11-14 minutes
                  </div>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                    Real-time assessment
                  </div>
                </div>
              </div>
              <div className="ml-6">
                <Link href="/test-library/speaking/ai-bot">
                  <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors flex items-center">
                    <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
                    Try AI Bot
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Tests Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:border-blue-300 transition-all duration-200"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(test.type)}`}>
                    {test.type}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                    {test.difficulty}
                  </span>
                </div>
                <div className="flex items-center text-blue-600">
                  <CpuChipIcon className="h-5 w-5 mr-1" />
                  <span className="text-sm font-semibold">AI</span>
                </div>
              </div>

              {/* Title and Description */}
              <h3 className="text-lg font-bold text-gray-900 mb-2">{test.title}</h3>
              <p className="text-gray-600 text-sm mb-4">{test.description}</p>

              {/* Topic */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Topic Covered:</h4>
                <div className="flex flex-wrap gap-1">
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                    {test.topics?.[0] || 'General Topics'}
                  </span>
                </div>
              </div>

              {/* Test Info */}
              <div className="space-y-2 text-sm text-gray-500 mb-4">
                <div className="flex items-center justify-between">
                  <span>Duration:</span>
                  <span className="font-semibold">{test.estimated_time}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Format:</span>
                  <span className="font-semibold">3 Parts</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Assessment:</span>
                  <span className="font-semibold text-blue-600">AI-Powered</span>
                </div>
              </div>

              {/* Action Button */}
              <Link href={`/test-library/speaking/${test.id}`}>
                <button className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center">
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start AI Speaking Test
                </button>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTests.length === 0 && (
          <div className="text-center py-12">
            <ChatBubbleLeftRightIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No speaking tests found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more tests.</p>
          </div>
        )}

        {/* AI Features Info */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">🤖 AI Speaking Test Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MicrophoneIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Voice Recognition</h3>
              <p className="text-sm text-gray-600">Advanced speech-to-text technology for accurate transcription</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Real-time Feedback</h3>
              <p className="text-sm text-gray-600">Instant AI feedback and suggestions during the test</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ChartBarIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Comprehensive Scoring</h3>
              <p className="text-sm text-gray-600">Detailed assessment across all IELTS speaking criteria</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CpuChipIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">AI Examiner</h3>
              <p className="text-sm text-gray-600">Intelligent conversation flow with natural follow-up questions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}