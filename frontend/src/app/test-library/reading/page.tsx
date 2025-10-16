'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  BookOpenIcon,
  ClockIcon,
  PlayIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ReadingTest {
  id: string
  title: string
  description: string
  duration: string
  difficulty: string
  questions: number
  passages: number
  completed: boolean
  score?: number
}

export default function ReadingTestPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [selectedTest, setSelectedTest] = useState<ReadingTest | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  const readingTests: ReadingTest[] = [
    {
      id: 'reading-1',
      title: 'IELTS Reading Test 1',
      description: 'Academic passages about climate change and renewable energy',
      duration: '60 minutes',
      difficulty: 'Intermediate',
      questions: 40,
      passages: 3,
      completed: false
    },
    {
      id: 'reading-2',
      title: 'IELTS Reading Test 2',
      description: 'General training passages about workplace communication',
      duration: '60 minutes',
      difficulty: 'Beginner',
      questions: 40,
      passages: 3,
      completed: true,
      score: 7.0
    },
    {
      id: 'reading-3',
      title: 'IELTS Reading Test 3',
      description: 'Academic passages about artificial intelligence and ethics',
      duration: '60 minutes',
      difficulty: 'Advanced',
      questions: 40,
      passages: 3,
      completed: false
    },
    {
      id: 'reading-4',
      title: 'IELTS Reading Test 4',
      description: 'General training passages about travel and tourism',
      duration: '60 minutes',
      difficulty: 'Intermediate',
      questions: 40,
      passages: 3,
      completed: true,
      score: 6.5
    }
  ]

  const handleStartTest = (test: ReadingTest) => {
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
                <BookOpenIcon className="h-8 w-8 mr-3 text-green-600" />
                IELTS Reading Tests
              </h1>
              <p className="text-gray-600 mt-1">
                Practice with authentic reading passages and improve your comprehension skills
              </p>
            </div>
            <div className="w-32"></div> {/* Spacer for centering */}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Test Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {readingTests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <BookOpenIcon className="h-6 w-6 text-green-600" />
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
                <div>{test.questions} questions • {test.passages} passages</div>
              </div>

              <button
                onClick={() => handleStartTest(test)}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] flex items-center justify-center"
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
                  Read the instructions carefully for each question type
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Skim through all passages first to get an overview
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Manage your time - aim for 20 minutes per passage
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Look for keywords and synonyms in the questions
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">During the Test</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Read questions before reading the passage
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Use scanning and skimming techniques effectively
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Answer questions in order when possible
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  Check your answers before moving to the next passage
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
