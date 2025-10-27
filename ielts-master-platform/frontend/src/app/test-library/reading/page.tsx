'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  EyeIcon,
  BookOpenIcon,
  ClockIcon,
  ArrowLeftIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  PlayIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ReadingTest {
  id: string
  title: string
  type: string
  difficulty: string
  estimated_time: string
  description: string
  book: number
  pdf_file: string
  total_passages: number
  total_questions: number
}

export default function ReadingTestsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [tests, setTests] = useState<ReadingTest[]>([])
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
      loadReadingTests()
    }
  }, [isAuthenticated])

  const loadReadingTests = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/reading`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const apiTests = await response.json()
        setTests(apiTests)
      } else {
        console.error('Failed to load reading tests')
        setTests([])
      }
    } catch (error) {
      console.error('Error loading reading tests:', error)
      setTests([])
    } finally {
      setLoading(false)
    }
  }

  const filteredTests = tests.filter(test => {
    const matchesFilter = filter === 'all' || test.type === filter
    const matchesDifficulty = difficulty === 'all' || test.difficulty === difficulty
    return matchesFilter && matchesDifficulty
  })

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
                <h1 className="text-3xl font-bold text-gray-900">IELTS Reading Tests</h1>
                <p className="text-gray-600 mt-1">Practice with authentic Cambridge IELTS reading passages</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Tests: {tests.length}</p>
              <p className="text-lg font-semibold text-green-600">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Test Type</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-green-500 focus:border-green-500"
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
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-green-500 focus:border-green-500"
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
              className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:border-green-300 transition-all duration-200"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                    {test.difficulty}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(test.type)}`}>
                    {test.type}
                  </span>
                </div>
                <div className="flex items-center text-green-600">
                  <EyeIcon className="h-5 w-5 mr-1" />
                  <span className="text-sm font-semibold">{test.total_passages}</span>
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
                  <span>Passages:</span>
                  <span className="font-semibold">{test.total_passages} passages</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Questions:</span>
                  <span className="font-semibold">{test.total_questions} questions</span>
                </div>
              </div>

              {/* PDF Preview */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-4 w-4 text-gray-500 mr-2" />
                  <span className="text-xs font-medium text-gray-600">PDF Material Available</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Complete reading test with passages and questions
                </p>
              </div>

              {/* Action Button */}
              <Link href={`/test-library/reading/${test.id}`}>
                <button className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center">
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start Reading Test
                </button>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTests.length === 0 && (
          <div className="text-center py-12">
            <EyeIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No tests found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more tests.</p>
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-12 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-8 border border-green-200">
          <h2 className="text-2xl font-bold text-green-900 mb-6 text-center">📖 Reading Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <ClockIcon className="h-5 w-5 text-green-600 mr-2" />
                Test Structure
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• 3 passages, 40 questions total</li>
                <li>• 60 minutes (20 minutes per passage)</li>
                <li>• Academic: Academic texts</li>
                <li>• General Training: Everyday texts</li>
                <li>• Various question types</li>
                <li>• No extra time for transferring answers</li>
              </ul>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <AcademicCapIcon className="h-5 w-5 text-green-600 mr-2" />
                Strategy Tips
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• Skim the passage first</li>
                <li>• Read questions before detailed reading</li>
                <li>• Look for keywords and synonyms</li>
                <li>• Don't spend too long on one question</li>
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