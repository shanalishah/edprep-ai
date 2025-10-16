'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  TrophyIcon,
  FireIcon,
  StarIcon,
  ArrowLeftIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'

interface ProgressData {
  progress: {
    essays_written: number
    average_score: number
    best_score: number
    improvement_rate: number
    skill_breakdown: {
      task_achievement: number
      coherence_cohesion: number
      lexical_resource: number
      grammatical_range: number
    }
    error_analysis: {
      l1_errors: number
      interlanguage_errors: number
      discourse_errors: number
    }
  }
  user_stats: {
    total_points: number
    level: number
    streak_days: number
    current_level: string
  }
}

export default function ProgressPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [progressData, setProgressData] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchProgressData()
    }
  }, [isAuthenticated])

  const fetchProgressData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('Authentication token not found')
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/user/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch progress data')
      }

      const data = await response.json()
      setProgressData(data)
    } catch (error: any) {
      console.error('Error fetching progress:', error)
      setError(error.message)
    } finally {
      setLoading(false)
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">❌ Error</div>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={() => router.push('/dashboard/home')}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  if (!progressData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <DocumentTextIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Progress Data</h2>
          <p className="text-gray-600 mb-4">Start writing essays to see your progress here!</p>
          <button
            onClick={() => router.push('/dashboard/write')}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Write Your First Essay
          </button>
        </div>
      </div>
    )
  }

  const { progress, user_stats } = progressData

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard/home')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeftIcon className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Your Progress</h1>
                <p className="text-gray-600 mt-1">Track your IELTS writing improvement</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Level {user_stats.level}</p>
              <p className="text-lg font-semibold text-primary-600">{user_stats.total_points} points</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Essays Written</p>
                <p className="text-2xl font-bold text-gray-900">{progress.essays_written}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <TrophyIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Best Score</p>
                <p className="text-2xl font-bold text-gray-900">{progress.best_score}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <StarIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{progress.average_score}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <FireIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Streak</p>
                <p className="text-2xl font-bold text-gray-900">{user_stats.streak_days} days</p>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Skill Breakdown */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Skill Breakdown</h2>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="space-y-6">
                {Object.entries(progress.skill_breakdown).map(([skill, score], index) => (
                  <motion.div
                    key={skill}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-primary-600 rounded-full mr-3"></div>
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {skill.replace('_', ' & ')}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-lg font-semibold text-gray-900 mr-2">{score}</span>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(score / 9) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Error Analysis */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Error Analysis</h2>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <span className="text-sm font-medium text-red-700">L1 Influence Errors</span>
                  <span className="text-lg font-semibold text-red-600">{progress.error_analysis.l1_errors}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <span className="text-sm font-medium text-orange-700">Interlanguage Errors</span>
                  <span className="text-lg font-semibold text-orange-600">{progress.error_analysis.interlanguage_errors}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <span className="text-sm font-medium text-yellow-700">Discourse Errors</span>
                  <span className="text-lg font-semibold text-yellow-600">{progress.error_analysis.discourse_errors}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Improvement Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8 bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-6 border border-primary-200"
        >
          <div className="flex items-start">
            <div className="p-3 bg-primary-100 rounded-lg">
              <TrendingUpIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-primary-900">💡 Improvement Tips</h3>
              <div className="text-primary-700 mt-2 space-y-2">
                <p>• <strong>Coherence & Cohesion:</strong> Focus on using linking words and organizing your ideas logically</p>
                <p>• <strong>Grammatical Range:</strong> Practice using complex sentence structures and varied tenses</p>
                <p>• <strong>Task Achievement:</strong> Make sure you address all parts of the question completely</p>
                <p>• <strong>Lexical Resource:</strong> Expand your vocabulary and avoid repetition</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
