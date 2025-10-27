'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  SpeakerWaveIcon,
  PlayIcon,
  PauseIcon,
  ArrowLeftIcon,
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ListeningTest {
  id: string
  title: string
  type: string
  difficulty: string
  estimated_time: string
  description: string
  book: number
  test_number: string
  sections: Array<{
    section: string
    audio_file: string
    duration: string
  }>
  total_sections: number
}

export default function ListeningTestsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [tests, setTests] = useState<ListeningTest[]>([])
  const [filter, setFilter] = useState<'all' | 'Easy' | 'Medium' | 'Hard'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      loadListeningTests()
    }
  }, [isAuthenticated])

  const loadListeningTests = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/listening`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const apiTests = await response.json()
        setTests(apiTests)
      } else {
        console.error('Failed to load listening tests')
        setTests([])
      }
    } catch (error) {
      console.error('Error loading listening tests:', error)
      setTests([])
    } finally {
      setLoading(false)
    }
  }

  const filteredTests = tests.filter(test => {
    return filter === 'all' || test.difficulty === filter
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <Link href="/test-library" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <ArrowLeftIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">IELTS Listening Tests</h1>
                <p className="text-gray-600 mt-1">Practice with real Cambridge IELTS audio recordings</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Tests: {tests.length}</p>
              <p className="text-lg font-semibold text-blue-600">
                Available: {filteredTests.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-200">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
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
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                    {test.difficulty}
                  </span>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {test.type}
                  </span>
                </div>
                <div className="flex items-center text-blue-600">
                  <SpeakerWaveIcon className="h-5 w-5 mr-1" />
                  <span className="text-sm font-semibold">{test.total_sections}</span>
                </div>
              </div>

              {/* Title and Description */}
              <h3 className="text-lg font-bold text-gray-900 mb-2">{test.title}</h3>
              <p className="text-gray-600 text-sm mb-4">{test.description}</p>

              {/* Test Info */}
              <div className="space-y-2 text-sm text-gray-500 mb-4">
                <div className="flex items-center justify-between">
                  <span>Estimated Time:</span>
                  <span className="font-semibold">{test.estimated_time}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Book:</span>
                  <span className="font-semibold">Cambridge IELTS {test.book}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Sections:</span>
                  <span className="font-semibold">{test.total_sections} sections</span>
                </div>
              </div>

              {/* Sections Preview */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <p className="text-xs font-medium text-gray-600 mb-2">Audio Sections:</p>
                <div className="space-y-1">
                  {test.sections.slice(0, 2).map((section, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{section.section}</span>
                      <span className="text-gray-500">{section.duration}</span>
                    </div>
                  ))}
                  {test.sections.length > 2 && (
                    <div className="text-xs text-gray-500">
                      +{test.sections.length - 2} more sections
                    </div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <Link href={`/test-library/listening/${test.id}`}>
                <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center">
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start Listening Test
                </button>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTests.length === 0 && (
          <div className="text-center py-12">
            <SpeakerWaveIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No tests found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more tests.</p>
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200">
          <h2 className="text-2xl font-bold text-blue-900 mb-6 text-center">🎧 Listening Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <ClockIcon className="h-5 w-5 text-blue-600 mr-2" />
                Test Structure
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• 4 sections, 40 questions total</li>
                <li>• 30 minutes listening + 10 minutes transfer</li>
                <li>• Section 1: Everyday conversation</li>
                <li>• Section 2: Monologue (social context)</li>
                <li>• Section 3: Academic discussion</li>
                <li>• Section 4: Academic lecture</li>
              </ul>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <AcademicCapIcon className="h-5 w-5 text-blue-600 mr-2" />
                Practice Tips
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• Listen to the instructions carefully</li>
                <li>• Use the time before each section wisely</li>
                <li>• Focus on keywords and synonyms</li>
                <li>• Don't leave any answers blank</li>
                <li>• Check spelling and grammar</li>
                <li>• Practice with authentic materials</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}