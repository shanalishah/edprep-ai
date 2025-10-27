'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  BookOpenIcon,
  SpeakerWaveIcon,
  EyeIcon,
  PencilIcon,
  MicrophoneIcon,
  ChartBarIcon,
  ClockIcon,
  StarIcon,
  PlayIcon,
  AcademicCapIcon,
  TrophyIcon,
  FireIcon,
  ArrowRightIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface TestCategory {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  color: string
  testCount: number
  difficulty: string
  estimatedTime: string
  href: string
}

export default function TestLibraryPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [userStats, setUserStats] = useState({
    totalTests: 0,
    averageScore: 0,
    bestScore: 0,
    streakDays: 0
  })

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserStats()
      fetchTestStats()
    }
  }, [isAuthenticated])

  const fetchTestStats = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setTestStats({
          listening_tests: data.listening_tests || 0,
          reading_tests: data.reading_tests || 0,
          writing_tests: data.writing_tests || 0,
          speaking_tests: data.speaking_tests || 0,
          total_tests: data.total_tests || 0
        })
      }
    } catch (error) {
      console.error('Error fetching test stats:', error)
    }
  }

  const fetchUserStats = async () => {
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
          totalTests: data.progress.essays_written || 0,
          averageScore: data.progress.average_score || 0,
          bestScore: data.progress.best_score || 0,
          streakDays: data.user_stats.streak_days || 0
        })
      }
    } catch (error) {
      console.error('Error fetching user stats:', error)
    }
  }

  const [testStats, setTestStats] = useState({
    listening_tests: 0,
    reading_tests: 0,
    writing_tests: 0,
    speaking_tests: 0,
    total_tests: 0
  })

  const testCategories: TestCategory[] = [
    {
      id: 'listening',
      title: 'IELTS Listening Tests',
      description: 'Practice with real audio recordings and improve your listening skills with authentic IELTS listening tests.',
      icon: <SpeakerWaveIcon className="h-8 w-8" />,
      color: 'bg-gradient-to-br from-blue-500 to-blue-600',
      testCount: testStats.listening_tests,
      difficulty: 'Mixed',
      estimatedTime: '30-40 min',
      href: '/test-library/listening'
    },
    {
      id: 'reading',
      title: 'IELTS Reading Tests',
      description: 'Practice with authentic reading passages and improve your comprehension skills with real IELTS reading tests.',
      icon: <EyeIcon className="h-8 w-8" />,
      color: 'bg-gradient-to-br from-green-500 to-green-600',
      testCount: testStats.reading_tests,
      difficulty: 'Mixed',
      estimatedTime: '60 min',
      href: '/test-library/reading'
    },
    {
      id: 'writing',
      title: 'IELTS Writing Tests',
      description: 'Get AI-powered feedback on your essays and improve your writing skills with comprehensive writing assessments.',
      icon: <PencilIcon className="h-8 w-8" />,
      color: 'bg-gradient-to-br from-purple-500 to-purple-600',
      testCount: testStats.writing_tests,
      difficulty: 'Mixed',
      estimatedTime: '60 min',
      href: '/test-library/writing'
    },
    {
      id: 'speaking',
      title: 'IELTS Speaking Tests',
      description: 'Practice speaking with AI-powered feedback and improve your fluency with realistic speaking assessments.',
      icon: <MicrophoneIcon className="h-8 w-8" />,
      color: 'bg-gradient-to-br from-orange-500 to-orange-600',
      testCount: testStats.speaking_tests,
      difficulty: 'Mixed',
      estimatedTime: '15-20 min',
      href: '/test-library/speaking'
    }
  ]

  const featuredTests = [
    {
      title: 'IELTS Academic Writing Task 2',
      description: 'Practice argumentative essays with AI feedback',
      difficulty: 'Intermediate',
      time: '60 min',
      score: 4.8,
      votes: 1247
    },
    {
      title: 'IELTS Listening Section 1',
      description: 'Everyday conversation practice',
      difficulty: 'Beginner',
      time: '30 min',
      score: 4.6,
      votes: 892
    },
    {
      title: 'IELTS Reading Academic',
      description: 'Academic reading comprehension',
      difficulty: 'Advanced',
      time: '60 min',
      score: 4.7,
      votes: 1156
    }
  ]

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading test library...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
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
                  Test Library
                </h1>
                <p className="text-gray-600 mt-1">
                  {testStats.total_tests}+ FREE IELTS practice tests with AI-powered feedback
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
                href="/analytics"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Analytics
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* User Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
                <p className="text-sm font-medium text-gray-600">Tests Taken</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.totalTests}</p>
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
                <p className="text-2xl font-bold text-gray-900">{userStats.averageScore?.toFixed(1) || 'N/A'}</p>
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
                <p className="text-2xl font-bold text-gray-900">{userStats.bestScore?.toFixed(1) || 'N/A'}</p>
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
                <FireIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Streak</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.streakDays} days</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Test Categories */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Practice All IELTS Skills</h2>
          <p className="text-lg text-gray-600 mb-8">
            Choose from our comprehensive collection of IELTS practice tests designed by certified examiners.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {testCategories.map((category, index) => (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-8 border border-white/20 hover:shadow-xl transition-all duration-300 group cursor-pointer"
                onClick={() => router.push(category.href)}
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center">
                    <div className={`p-4 ${category.color} rounded-xl group-hover:scale-110 transition-transform duration-200`}>
                      {category.icon}
                    </div>
                    <div className="ml-4">
                      <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{category.title}</h3>
                      <p className="text-gray-600 mt-1">{category.description}</p>
                    </div>
                  </div>
                  <ArrowRightIcon className="h-6 w-6 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all duration-200" />
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-600">Tests</p>
                    <p className="text-lg font-bold text-gray-900">{category.testCount}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-600">Difficulty</p>
                    <p className="text-lg font-bold text-gray-900">{category.difficulty}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-600">Time</p>
                    <p className="text-lg font-bold text-gray-900">{category.estimatedTime}</p>
                  </div>
                </div>
                
                <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
                  Start Practice
                </button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Featured Tests */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Featured Tests</h2>
          <p className="text-lg text-gray-600 mb-8">
            Most popular tests with highest ratings from our community.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {featuredTests.map((test, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-white/20 hover:shadow-xl transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-semibold px-3 py-1 rounded-full">
                    {test.difficulty}
                  </span>
                  <div className="flex items-center">
                    <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="ml-1 text-sm font-medium text-gray-600">{test.score}</span>
                  </div>
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2">{test.title}</h3>
                <p className="text-gray-600 mb-4">{test.description}</p>
                
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {test.time}
                  </div>
                  <span className="text-sm text-gray-500">({test.votes} votes)</span>
                </div>
                
                <button className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-2 px-4 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition-all duration-200">
                  <PlayIcon className="h-4 w-4 inline mr-2" />
                  Start Test
                </button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white"
        >
          <h3 className="text-3xl font-bold mb-4">Ready to Boost Your IELTS Score?</h3>
          <p className="text-lg text-blue-100 mb-6">
            Join thousands of successful candidates who improved their band scores with our practice tests.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/test-library/writing"
              className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
            >
              <PencilIcon className="mr-2 h-5 w-5" />
              Start Writing Test
            </Link>
            <Link
              href="/test-library/listening"
              className="inline-flex items-center border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-all duration-200"
            >
              <SpeakerWaveIcon className="mr-2 h-5 w-5" />
              Start Listening Test
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}