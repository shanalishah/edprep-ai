'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  ChartBarIcon,
  TrophyIcon,
  FireIcon,
  StarIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  PencilIcon,
  SpeakerWaveIcon,
  MicrophoneIcon,
  AcademicCapIcon,
  CalendarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  BookOpenIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface AnalyticsData {
  overall: {
    totalTests: number
    averageScore: number
    bestScore: number
    improvementRate: number
  }
  skills: {
    listening: { score: number; trend: 'up' | 'down' | 'stable' }
    reading: { score: number; trend: 'up' | 'down' | 'stable' }
    writing: { score: number; trend: 'up' | 'down' | 'stable' }
    speaking: { score: number; trend: 'up' | 'down' | 'stable' }
  }
  recentTests: Array<{
    id: string
    type: string
    score: number
    date: string
  }>
}

export default function AnalyticsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchAnalyticsData()
    }
  }, [isAuthenticated])

  const fetchAnalyticsData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/user/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Transform the data to match our analytics interface
        setAnalyticsData({
          overall: {
            totalTests: data.progress.essays_written || 0,
            averageScore: data.progress.average_score || 0,
            bestScore: data.progress.best_score || 0,
            improvementRate: 15.2 // Mock data
          },
          skills: {
            listening: { score: 7.5, trend: 'up' },
            reading: { score: 7.0, trend: 'stable' },
            writing: { score: data.progress.average_score || 6.5, trend: 'up' },
            speaking: { score: 6.8, trend: 'down' }
          },
          recentTests: [
            { id: '1', type: 'Writing Task 2', score: data.progress.best_score || 7.0, date: '2025-01-15' },
            { id: '2', type: 'Writing Task 1', score: 6.5, date: '2025-01-14' },
            { id: '3', type: 'Reading Test', score: 7.0, date: '2025-01-13' }
          ]
        })
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>
    }
  }

  const getTrendColor = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <span className="text-white font-bold text-xl">E</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Analytics Dashboard
                </h1>
                <p className="text-gray-600 mt-1">
                  Track your IELTS progress and performance insights
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/dashboard/home"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Dashboard
              </Link>
              <Link 
                href="/test-library"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Test Library
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl">
                <BookOpenIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Tests</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData?.overall.totalTests || 0}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl">
                <ChartBarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData?.overall.averageScore?.toFixed(1) || 'N/A'}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl">
                <TrophyIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Best Score</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData?.overall.bestScore?.toFixed(1) || 'N/A'}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
                <ArrowTrendingUpIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Improvement</p>
                <p className="text-2xl font-bold text-gray-900">+{analyticsData?.overall.improvementRate || 0}%</p>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Skills Breakdown */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Skills Performance</h2>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {analyticsData?.skills && Object.entries(analyticsData.skills).map(([skill, data], index) => (
                  <motion.div
                    key={skill}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-6 rounded-xl border border-gray-200 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        {skill === 'listening' && <SpeakerWaveIcon className="h-6 w-6 text-blue-600 mr-3" />}
                        {skill === 'reading' && <EyeIcon className="h-6 w-6 text-green-600 mr-3" />}
                        {skill === 'writing' && <PencilIcon className="h-6 w-6 text-purple-600 mr-3" />}
                        {skill === 'speaking' && <MicrophoneIcon className="h-6 w-6 text-orange-600 mr-3" />}
                        <h3 className="text-lg font-semibold text-gray-900 capitalize">{skill}</h3>
                      </div>
                      {getTrendIcon(data.trend)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-3xl font-bold text-gray-900">{data.score.toFixed(1)}</span>
                      <span className={`text-sm font-medium ${getTrendColor(data.trend)}`}>
                        {data.trend === 'up' ? 'Improving' : data.trend === 'down' ? 'Declining' : 'Stable'}
                      </span>
                    </div>
                    <div className="mt-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(data.score / 9) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Tests */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Tests</h2>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              {analyticsData?.recentTests && analyticsData.recentTests.length > 0 ? (
                <ul className="space-y-4">
                  {analyticsData.recentTests.map((test, index) => (
                    <motion.li
                      key={test.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div>
                        <p className="font-medium text-gray-800">{test.type}</p>
                        <p className="text-sm text-gray-500">{test.date}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">{test.score.toFixed(1)}</p>
                        <div className="flex items-center">
                          <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                          <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                          <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                          <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                          <StarIcon className="h-4 w-4 text-gray-300" />
                        </div>
                      </div>
                    </motion.li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8">
                  <BookOpenIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No tests completed yet.</p>
                  <p className="text-sm text-gray-400 mt-1">Start practicing to see your results here!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Performance Insights */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance Insights</h2>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-center p-6"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <SparklesIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Strong Areas</h3>
                <p className="text-gray-600">Your writing skills show consistent improvement. Keep practicing to maintain this momentum.</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-center p-6"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <AcademicCapIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Focus Areas</h3>
                <p className="text-gray-600">Speaking skills need attention. Consider practicing more speaking exercises and pronunciation.</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center p-6"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <ChartBarIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommendations</h3>
                <p className="text-gray-600">Take more practice tests to improve your overall band score and identify specific weaknesses.</p>
              </motion.div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white"
          >
            <h3 className="text-2xl font-bold mb-4">Ready to Improve Your Performance?</h3>
            <p className="text-lg text-blue-100 mb-6">
              Take a practice test to update your analytics and track your progress.
            </p>
            <Link
              href="/test-library"
              className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
            >
              <BookOpenIcon className="mr-2 h-5 w-5" />
              Take Practice Test
            </Link>
          </motion.div>
        </div>
      </div>
    </div>
  )
}