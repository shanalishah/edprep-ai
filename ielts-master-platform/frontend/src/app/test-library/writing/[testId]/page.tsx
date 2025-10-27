'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  PencilIcon,
  ClockIcon,
  ArrowLeftIcon as LeftArrowIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface WritingTest {
  id: string
  title: string
  type: 'Academic' | 'General Training'
  difficulty: 'Easy' | 'Medium' | 'Hard'
  estimated_time: string
  description: string
  book: number | null
  task_type: 'Task 1' | 'Task 2' | 'Task 1 & Task 2'
  word_count: number | string
  prompt: string
  sample_answer: string | null
  pdf_file: string | null
}

interface TestSession {
  testId: string
  startTime: Date
  timeRemaining: number
  task1Answer: string
  task2Answer: string
  isCompleted: boolean
  score?: {
    task1?: number
    task2?: number
    overall?: number
  }
  feedback?: any
}

export default function WritingTestPage({ params }: { params: { testId: string } }) {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [test, setTest] = useState<WritingTest | null>(null)
  const [session, setSession] = useState<TestSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRemaining, setTimeRemaining] = useState(3600) // 60 minutes in seconds
  const [showResults, setShowResults] = useState(false)
  const [currentTask, setCurrentTask] = useState<'task1' | 'task2'>('task1')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      loadTestData()
    }
  }, [isAuthenticated, params.testId])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (session && !session.isCompleted && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleCompleteTest()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [session, timeRemaining])

  const loadTestData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/writing`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const tests = await response.json()
        const currentTest = tests.find((t: WritingTest) => t.id === params.testId)
        
        if (currentTest) {
          setTest(currentTest)
          initializeSession(currentTest)
        }
      }
    } catch (error) {
      console.error('Error loading test data:', error)
    } finally {
      setLoading(false)
    }
  }

  const initializeSession = (testData: WritingTest) => {
    const timeLimit = testData.task_type === 'Task 1' ? 1200 : // 20 minutes for Task 1
                     testData.task_type === 'Task 2' ? 2400 : // 40 minutes for Task 2
                     3600 // 60 minutes for both tasks
    
    const newSession: TestSession = {
      testId: testData.id,
      startTime: new Date(),
      timeRemaining: timeLimit,
      task1Answer: '',
      task2Answer: '',
      isCompleted: false
    }
    setSession(newSession)
    setTimeRemaining(timeLimit)
  }

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const countWords = (text: string): number => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length
  }

  const handleAnswerChange = (task: 'task1' | 'task2', answer: string) => {
    if (!session) return
    
    setSession(prev => prev ? {
      ...prev,
      [task === 'task1' ? 'task1Answer' : 'task2Answer']: answer
    } : null)
  }

  const handleCompleteTest = async () => {
    if (!session || !test || isSubmitting) return

    setIsSubmitting(true)

    try {
      // Submit Task 1 if it exists and has content
      let task1Score = null
      if (test.task_type === 'Task 1' || test.task_type === 'Task 1 & Task 2') {
        if (session.task1Answer.trim()) {
          const task1Response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/essays/assess`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              prompt: test.prompt,
              essay: session.task1Answer,
              task_type: 'Task 1'
            })
          })

          if (task1Response.ok) {
            const task1Result = await task1Response.json()
            task1Score = task1Result.overall_band_score
          }
        }
      }

      // Submit Task 2 if it exists and has content
      let task2Score = null
      if (test.task_type === 'Task 2' || test.task_type === 'Task 1 & Task 2') {
        if (session.task2Answer.trim()) {
          const task2Response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/essays/assess`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              prompt: test.prompt,
              essay: session.task2Answer,
              task_type: 'Task 2'
            })
          })

          if (task2Response.ok) {
            const task2Result = await task2Response.json()
            task2Score = task2Result.overall_band_score
          }
        }
      }

      // Calculate overall score
      const scores = [task1Score, task2Score].filter(score => score !== null)
      const overallScore = scores.length > 0 ? scores.reduce((sum, score) => sum + score, 0) / scores.length : 0

      const completedSession: TestSession = {
        ...session,
        isCompleted: true,
        score: {
          task1: task1Score,
          task2: task2Score,
          overall: overallScore
        }
      }

      setSession(completedSession)
      setShowResults(true)

      // Save results to backend
      const token = localStorage.getItem('access_token')
      if (token) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/test-sessions/complete`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            testId: test.id,
            testType: 'writing',
            score: overallScore,
            answers: {
              task1: session.task1Answer,
              task2: session.task2Answer
            },
            timeSpent: (test.task_type === 'Task 1' ? 1200 : test.task_type === 'Task 2' ? 2400 : 3600) - timeRemaining
          })
        })
      }
    } catch (error) {
      console.error('Error submitting test:', error)
    } finally {
      setIsSubmitting(false)
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

  const getWordCountColor = (current: number, target: number) => {
    if (current < target * 0.8) return 'text-red-600'
    if (current < target) return 'text-yellow-600'
    return 'text-green-600'
  }

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

  if (!test || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <PencilIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Test not found</h3>
          <p className="text-gray-600">The writing test you\'re looking for doesn\'t exist.</p>
        </div>
      </div>
    )
  }

  if (showResults) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-6">
              <div className="flex items-center">
                <Link href="/test-library/writing" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                  <LeftArrowIcon className="h-6 w-6" />
                </Link>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Test Results</h1>
                  <p className="text-gray-600">{test.title}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">
                  Overall Score: {session.score?.overall?.toFixed(1)}
                </div>
                <p className="text-sm text-gray-500">
                  {test.task_type} Completed
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Test Completed!</h2>
              <p className="text-gray-600">You have successfully completed the writing test.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{session.score?.overall?.toFixed(1)}</div>
                <div className="text-sm text-blue-800">Overall Band Score</div>
              </div>
              {session.score?.task1 && (
                <div className="bg-green-50 rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">{session.score.task1.toFixed(1)}</div>
                  <div className="text-sm text-green-800">Task 1 Score</div>
                </div>
              )}
              {session.score?.task2 && (
                <div className="bg-purple-50 rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">{session.score.task2.toFixed(1)}</div>
                  <div className="text-sm text-purple-800">Task 2 Score</div>
                </div>
              )}
            </div>

            <div className="flex justify-center space-x-4">
              <Link href="/test-library/writing">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Back to Writing Tests
                </button>
              </Link>
              <Link href="/test-library">
                <button className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                  Test Library
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const currentAnswer = currentTask === 'task1' ? session.task1Answer : session.task2Answer
  const currentWordCount = countWords(currentAnswer)
  const targetWordCount = typeof test.word_count === 'string' ? 
    parseInt(test.word_count.split('-')[0]) : test.word_count

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <Link href="/test-library/writing" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <LeftArrowIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
                <p className="text-sm text-gray-600">
                  {test.task_type} • {test.type}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <ClockIcon className="h-5 w-5 text-gray-500" />
                <span className={`text-lg font-mono ${timeRemaining < 300 ? 'text-red-600' : 'text-gray-900'}`}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                  {test.difficulty}
                </span>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {test.type}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Task Navigation & Instructions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              {/* Task Navigation */}
              {(test.task_type === 'Task 1 & Task 2') && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Tasks</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => setCurrentTask('task1')}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        currentTask === 'task1'
                          ? 'bg-blue-50 border-blue-300 text-blue-900'
                          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="font-semibold">Task 1</div>
                      <div className="text-sm text-gray-600">150 words • 20 minutes</div>
                    </button>
                    <button
                      onClick={() => setCurrentTask('task2')}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        currentTask === 'task2'
                          ? 'bg-blue-50 border-blue-300 text-blue-900'
                          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="font-semibold">Task 2</div>
                      <div className="text-sm text-gray-600">250 words • 40 minutes</div>
                    </button>
                  </div>
                </div>
              )}

              {/* Instructions */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Instructions</h3>
                <div className="text-sm text-gray-700 space-y-2">
                  <p><strong>Task:</strong> {test.task_type}</p>
                  <p><strong>Time:</strong> {test.estimated_time}</p>
                  <p><strong>Words:</strong> {test.word_count} minimum</p>
                  <p><strong>Type:</strong> {test.type}</p>
                </div>
              </div>

              {/* Word Count */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Word Count</h3>
                <div className="text-center">
                  <div className={`text-3xl font-bold ${getWordCountColor(currentWordCount, targetWordCount)}`}>
                    {currentWordCount}
                  </div>
                  <div className="text-sm text-gray-600">
                    / {targetWordCount} words minimum
                  </div>
                  {currentWordCount < targetWordCount && (
                    <div className="mt-2 text-xs text-red-600 flex items-center justify-center">
                      <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                      Below minimum word count
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleCompleteTest}
                disabled={isSubmitting || (!session.task1Answer.trim() && !session.task2Answer.trim())}
                className="w-full py-3 px-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
                    Submit Test
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Writing Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              {/* Prompt */}
              <div className="mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  {test.task_type} Prompt
                </h2>
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
                  <p className="text-gray-800 leading-relaxed">
                    {test.prompt}
                  </p>
                </div>
              </div>

              {/* Writing Area */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Your Answer
                  </h3>
                  <div className="text-sm text-gray-500">
                    {currentWordCount} words
                  </div>
                </div>
                
                <textarea
                  ref={textareaRef}
                  value={currentAnswer}
                  onChange={(e) => handleAnswerChange(currentTask, e.target.value)}
                  placeholder={`Write your ${test.task_type} answer here...`}
                  className="w-full h-96 p-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 resize-none font-mono text-sm leading-relaxed"
                  style={{ lineHeight: '1.6' }}
                />
              </div>

              {/* Tips */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-2">Writing Tips</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Plan your essay before writing</li>
                  <li>• Use clear paragraph structure</li>
                  <li>• Include relevant examples and details</li>
                  <li>• Check your grammar and vocabulary</li>
                  <li>• Stay within the word count requirements</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


