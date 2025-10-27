'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  MicrophoneIcon,
  ClockIcon,
  PlayIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface SpeakingTest {
  id: string
  title: string
  description: string
  duration: string
  difficulty: string
  parts: number
  completed: boolean
  score?: number
}

export default function SpeakingTestPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [selectedTest, setSelectedTest] = useState<SpeakingTest | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  const speakingTests: SpeakingTest[] = [
    {
      id: 'speaking-1',
      title: 'IELTS Speaking Test 1',
      description: 'Practice speaking about familiar topics and personal experiences',
      duration: '11-14 minutes',
      difficulty: 'Intermediate',
      parts: 3,
      completed: false
    },
    {
      id: 'speaking-2',
      title: 'IELTS Speaking Test 2',
      description: 'Practice describing objects, places, and events in detail',
      duration: '11-14 minutes',
      difficulty: 'Beginner',
      parts: 3,
      completed: true,
      score: 6.5
    },
    {
      id: 'speaking-3',
      title: 'IELTS Speaking Test 3',
      description: 'Practice discussing abstract topics and expressing opinions',
      duration: '11-14 minutes',
      difficulty: 'Advanced',
      parts: 3,
      completed: false
    },
    {
      id: 'speaking-4',
      title: 'IELTS Speaking Test 4',
      description: 'Practice speaking about work, studies, and future plans',
      duration: '11-14 minutes',
      difficulty: 'Intermediate',
      parts: 3,
      completed: true,
      score: 7.0
    }
  ]

  const handleStartTest = (test: SpeakingTest) => {
    setSelectedTest(test)
    // In a real app, this would start the actual test
    console.log('Starting test:', test.title)
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
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
              <Link 
                href="/test-library"
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5 mr-2" />
                Back to Test Library
              </Link>
            </div>
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <MicrophoneIcon className="h-8 w-8 mr-3 text-purple-600" />
                IELTS Speaking Tests
              </h1>
              <p className="text-gray-600 mt-1">
                Practice speaking with AI-powered feedback and improve your fluency
              </p>
            </div>
            <div className="w-32"></div> {/* Spacer for centering */}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Test Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {speakingTests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <MicrophoneIcon className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{test.title}</h3>
                    <p className="text-sm text-gray-500">{test.difficulty}</p>
                  </div>
                </div>
                {test.completed && (
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-1" />
                    <span className="text-sm font-medium text-green-600">{test.score}</span>
                  </div>
                )}
              </div>

              <p className="text-gray-600 mb-4">{test.description}</p>

              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <div className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  {test.duration}
                </div>
                <div>{test.parts} parts</div>
              </div>

              <button
                onClick={() => handleStartTest(test)}
                className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] flex items-center justify-center"
              >
                <PlayIcon className="h-5 w-5 mr-2" />
                {test.completed ? 'Retake Test' : 'Start Test'}
              </button>
            </motion.div>
          ))}
        </div>

        {/* Test Instructions */}
        <div className="mt-12 bg-white rounded-xl shadow-sm p-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Test Instructions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Before You Start</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Ensure your microphone is working properly
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Find a quiet environment with no background noise
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Have a pen and paper ready for Part 2 notes
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Relax and speak naturally - it's a conversation
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">During the Test</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Listen carefully to the examiner's questions
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Give detailed answers - don't just say yes or no
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Use the 1-minute preparation time in Part 2 wisely
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Express your opinions clearly in Part 3
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Speaking Test Structure */}
        <div className="mt-8 bg-white rounded-xl shadow-sm p-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Speaking Test Structure</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="p-4 bg-blue-100 rounded-lg mb-4">
                <span className="text-2xl font-bold text-blue-600">Part 1</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Introduction & Interview</h3>
              <p className="text-gray-600 text-sm">4-5 minutes</p>
              <p className="text-gray-600 text-sm mt-2">Questions about yourself, home, work, studies, and interests</p>
            </div>
            <div className="text-center">
              <div className="p-4 bg-green-100 rounded-lg mb-4">
                <span className="text-2xl font-bold text-green-600">Part 2</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Individual Long Turn</h3>
              <p className="text-gray-600 text-sm">3-4 minutes</p>
              <p className="text-gray-600 text-sm mt-2">Speak for 1-2 minutes on a given topic with 1 minute preparation</p>
            </div>
            <div className="text-center">
              <div className="p-4 bg-purple-100 rounded-lg mb-4">
                <span className="text-2xl font-bold text-purple-600">Part 3</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Two-way Discussion</h3>
              <p className="text-gray-600 text-sm">4-5 minutes</p>
              <p className="text-gray-600 text-sm mt-2">Abstract discussion related to the topic in Part 2</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}






