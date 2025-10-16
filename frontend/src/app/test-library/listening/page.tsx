'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  SpeakerWaveIcon,
  ClockIcon,
  PlayIcon,
  PauseIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ListeningTest {
  id: string
  title: string
  description: string
  duration: string
  difficulty: string
  questions: number
  audioUrl?: string
  completed: boolean
  score?: number
}

export default function ListeningTestPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [selectedTest, setSelectedTest] = useState<ListeningTest | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  const listeningTests: ListeningTest[] = [
    {
      id: 'listening-1',
      title: 'IELTS Listening Test 1',
      description: 'Academic conversation about university accommodation',
      duration: '30 minutes',
      difficulty: 'Intermediate',
      questions: 40,
      completed: false
    },
    {
      id: 'listening-2',
      title: 'IELTS Listening Test 2',
      description: 'General conversation about travel arrangements',
      duration: '30 minutes',
      difficulty: 'Beginner',
      questions: 40,
      completed: true,
      score: 7.5
    },
    {
      id: 'listening-3',
      title: 'IELTS Listening Test 3',
      description: 'Academic lecture about environmental science',
      duration: '30 minutes',
      difficulty: 'Advanced',
      questions: 40,
      completed: false
    },
    {
      id: 'listening-4',
      title: 'IELTS Listening Test 4',
      description: 'General conversation about job interview',
      duration: '30 minutes',
      difficulty: 'Intermediate',
      questions: 40,
      completed: true,
      score: 6.5
    }
  ]

  const handleStartTest = (test: ListeningTest) => {
    setSelectedTest(test)
    // In a real app, this would start the actual test
    console.log('Starting test:', test.title)
  }

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
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
                <SpeakerWaveIcon className="h-8 w-8 mr-3 text-blue-600" />
                IELTS Listening Tests
              </h1>
              <p className="text-gray-600 mt-1">
                Practice with real audio recordings and improve your listening skills
              </p>
            </div>
            <div className="w-32"></div> {/* Spacer for centering */}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Test Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {listeningTests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <SpeakerWaveIcon className="h-6 w-6 text-blue-600" />
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
                <div>{test.questions} questions</div>
              </div>

              <button
                onClick={() => handleStartTest(test)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] flex items-center justify-center"
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
                  Ensure you have good quality headphones or speakers
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Find a quiet environment with no distractions
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Have a pen and paper ready for notes
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Read the questions before the audio starts
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">During the Test</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Listen carefully to the entire recording
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Answer questions as you listen
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Use the 10-minute transfer time wisely
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Check your spelling and grammar
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
