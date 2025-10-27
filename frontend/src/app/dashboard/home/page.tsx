'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  BookOpenIcon, 
  ChartBarIcon, 
  SparklesIcon, 
  UserGroupIcon,
  ClockIcon,
  TrophyIcon,
  FireIcon,
  StarIcon,
  ArrowTrendingUpIcon,
  UserIcon,
  AcademicCapIcon,
  LightBulbIcon,
  DocumentTextIcon,
  PencilIcon,
  ArrowRightIcon,
  PlayIcon
} from '@heroicons/react/24/outline'

export default function DashboardHomePage() {
  const { isAuthenticated, user, logout, loading: authLoading } = useAuth()
  const router = useRouter()
  const [userStats, setUserStats] = useState({
    essaysWritten: 0,
    averageScore: 0,
    bestScore: 0,
    streakDays: 0,
    level: 1,
    totalPoints: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  // Fetch real progress data
  useEffect(() => {
    if (isAuthenticated) {
      fetchProgressData()
    }
  }, [isAuthenticated])

  const fetchProgressData = async () => {
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
        setUserStats({
          essaysWritten: data.progress.essays_written || 0,
          averageScore: data.progress.average_score || 0,
          bestScore: data.progress.best_score || 0,
          streakDays: data.user_stats.streak_days || 0,
          level: data.user_stats.level || 1,
          totalPoints: data.user_stats.total_points || 0
        })
      }
    } catch (error) {
      console.error('Error fetching progress:', error)
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  const userName = user?.full_name || user?.username || user?.email?.split('@')[0] || 'Learner'

  const quickActions = [
    {
      title: 'Write Essay',
      description: 'Start a new IELTS writing task',
      icon: PencilIcon,
      color: 'bg-gradient-to-br from-blue-500 to-blue-600',
      href: '/dashboard/write'
    },
    {
      title: 'Test Library',
      description: '100+ FREE IELTS practice tests',
      icon: BookOpenIcon,
      color: 'bg-gradient-to-br from-purple-500 to-purple-600',
      href: '/test-library'
    },
    {
      title: 'Mentorship',
      description: 'Connect with mentors and mentees',
      icon: UserGroupIcon,
      color: 'bg-gradient-to-br from-orange-500 to-orange-600',
      href: '/mentorship'
    },
    {
      title: 'View Progress',
      description: 'Check your improvement over time',
      icon: ChartBarIcon,
      color: 'bg-gradient-to-br from-green-500 to-green-600',
      href: '/dashboard/progress'
    },
    {
      title: 'Analytics',
      description: 'Detailed progress insights',
      icon: ChartBarIcon,
      color: 'bg-gradient-to-br from-indigo-500 to-indigo-600',
      href: '/analytics'
    }
  ]

  const recentActivities = [
    { type: 'essay', title: 'Technology Impact Essay', score: 7.5, date: '2 hours ago' },
    { type: 'practice', title: 'Task 1 Practice', score: 6.5, date: '1 day ago' },
    { type: 'feedback', title: 'Grammar Review', score: null, date: '2 days ago' }
  ]

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
                  Welcome back, {userName}! 👋
                </h1>
                <p className="text-gray-600 mt-1">
                  Here's your personalized IELTS preparation overview.
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/test-library"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Test Library
              </Link>
              <Link 
                href="/writing-coach"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Writing Coach
              </Link>
              <Link 
                href="/mentorship"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Mentorship
              </Link>
              <Link 
                href="/analytics"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Analytics
              </Link>
              <button
                onClick={logout}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* User Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl">
                <PencilIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Essays Written</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.essaysWritten}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl">
                <TrophyIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Best Score</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.bestScore || 'N/A'}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl">
                <FireIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Streak</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.streakDays} days</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
                <StarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.averageScore || 'N/A'}</p>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {quickActions.map((action, index) => (
                <motion.div
                  key={action.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300 cursor-pointer group"
                  onClick={() => router.push(action.href)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`p-4 ${action.color} rounded-xl group-hover:scale-110 transition-transform duration-200`}>
                        <action.icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="ml-4">
                        <p className="text-lg font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">{action.title}</p>
                        <p className="text-sm text-gray-500">{action.description}</p>
                      </div>
                    </div>
                    <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all duration-200" />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Activity</h2>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
              {recentActivities.length > 0 ? (
                <ul className="space-y-4">
                  {recentActivities.map((activity, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.15 }}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-6 w-6 text-gray-500 mr-3" />
                        <div>
                          <p className="font-medium text-gray-800">{activity.title}</p>
                          <p className="text-sm text-gray-500">
                            {activity.score ? `Score: ${activity.score} | ` : ''}
                            {activity.date}
                          </p>
                        </div>
                      </div>
                      <ArrowTrendingUpIcon className="h-5 w-5 text-gray-400" />
                    </motion.li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8">
                  <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No recent activity.</p>
                  <p className="text-sm text-gray-400 mt-1">Start practicing to see your progress here!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Personalized Learning Tips */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Personalized Learning Tips</h2>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20">
            <ul className="space-y-6">
              <motion.li 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="flex items-start"
              >
                <div className="p-2 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg mr-4 flex-shrink-0">
                  <LightBulbIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">Focus on Coherence & Cohesion</h3>
                  <p className="text-gray-700">
                    Your recent essays show room for improvement in linking ideas. Try using more transition words like "however," "therefore," and "in addition."
                  </p>
                </div>
              </motion.li>
              <motion.li 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="flex items-start"
              >
                <div className="p-2 bg-gradient-to-br from-blue-400 to-blue-500 rounded-lg mr-4 flex-shrink-0">
                  <LightBulbIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">Expand Vocabulary</h3>
                  <p className="text-gray-700">
                    Challenge yourself to use 3-5 new academic words in each essay. Use a thesaurus, but ensure the words fit the context naturally.
                  </p>
                </div>
              </motion.li>
              <motion.li 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="flex items-start"
              >
                <div className="p-2 bg-gradient-to-br from-green-400 to-green-500 rounded-lg mr-4 flex-shrink-0">
                  <LightBulbIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">Grammar Review</h3>
                  <p className="text-gray-700">
                    Pay close attention to subject-verb agreement and complex sentence structures. Practice identifying and correcting common errors in your writing.
                  </p>
                </div>
              </motion.li>
            </ul>
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
            <h3 className="text-2xl font-bold mb-4">Ready to Improve Your IELTS Score?</h3>
            <p className="text-lg text-blue-100 mb-6">
              Take a practice test and get instant AI-powered feedback to boost your performance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/test-library"
                className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
              >
                <PlayIcon className="mr-2 h-5 w-5" />
                Start Practice Test
              </Link>
              <Link
                href="/dashboard/write"
                className="inline-flex items-center border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-all duration-200"
              >
                <PencilIcon className="mr-2 h-5 w-5" />
                Write Essay
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}