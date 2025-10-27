'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Tab } from '@headlessui/react'
import { 
  BookOpenIcon, 
  ChartBarIcon, 
  SparklesIcon, 
  ClockIcon,
  TrophyIcon,
  ArrowLeftIcon,
  PencilIcon
} from '@heroicons/react/24/outline'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'

interface ErrorAnalysis {
  l1_influenced: string[]
  interlanguage: string[]
  discourse_management: string[]
}

interface FeedbackDetail {
  detailed_feedback: string
  suggestions: string[]
  error_analysis: ErrorAnalysis
}

interface ScoringResult {
  task_achievement: number
  coherence_cohesion: number
  lexical_resource: number
  grammatical_range: number
  overall_band_score: number
  feedback: FeedbackDetail
  confidence: number
  scoring_method: string
  timestamp: string
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function WritePage() {
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [essay, setEssay] = useState('')
  const [prompt, setPrompt] = useState('Some people believe that technology has made our lives more complicated, while others think it has made life easier. Discuss both views and give your opinion.')
  const [result, setResult] = useState<ScoringResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState(0)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  const handleSubmit = async () => {
    if (!essay.trim()) {
      setError('Please write an essay before submitting.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.')
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/essays/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          prompt,
          essay,
          task_type: 'Task 2',
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Assessment failed')
      }

      const data = await response.json()
      setResult({
        ...data.scores,
        feedback: data.feedback,
        confidence: data.assessment_metadata.confidence,
        scoring_method: data.assessment_metadata.assessment_method,
        timestamp: new Date().toISOString()
      })
      
      toast.success('Essay assessed successfully!')
      
    } catch (error: any) {
      console.error('Assessment error:', error)
      setError(error.message || 'Failed to assess essay. Please try again.')
      toast.error(error.message || 'Assessment failed')
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
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
              <button
                onClick={() => router.push('/dashboard/home')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeftIcon className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Writing Assessment</h1>
                <p className="text-gray-600 mt-1">Practice your IELTS writing skills</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Word Count</p>
                <p className="text-lg font-semibold text-primary-600">{essay.split(' ').filter(word => word.length > 0).length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Writing Section */}
          <div className="space-y-6">
            {/* Prompt */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BookOpenIcon className="h-5 w-5 mr-2 text-primary-600" />
                Writing Task
              </h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 leading-relaxed">{prompt}</p>
              </div>
            </div>

            {/* Essay Input */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <PencilIcon className="h-5 w-5 mr-2 text-primary-600" />
                Your Essay
              </h2>
              <textarea
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                placeholder="Write your essay here..."
                className="w-full h-96 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              />
              <div className="mt-4 flex justify-between items-center">
                <p className="text-sm text-gray-500">
                  Minimum 250 words recommended for Task 2
                </p>
                <button
                  onClick={handleSubmit}
                  disabled={loading || !essay.trim()}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Assessing...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4 mr-2" />
                      Assess Essay
                    </>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Scores Overview */}
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <TrophyIcon className="h-5 w-5 mr-2 text-primary-600" />
                    Assessment Results
                  </h2>
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center p-4 bg-primary-50 rounded-lg">
                      <p className="text-3xl font-bold text-primary-600">{result.overall_band_score}</p>
                      <p className="text-sm text-gray-600">Overall Band Score</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <p className="text-3xl font-bold text-green-600">{Math.round(result.confidence * 100)}%</p>
                      <p className="text-sm text-gray-600">Confidence</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Task Achievement</span>
                      <span className="text-lg font-semibold text-gray-900">{result.task_achievement}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Coherence & Cohesion</span>
                      <span className="text-lg font-semibold text-gray-900">{result.coherence_cohesion}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Lexical Resource</span>
                      <span className="text-lg font-semibold text-gray-900">{result.lexical_resource}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Grammatical Range</span>
                      <span className="text-lg font-semibold text-gray-900">{result.grammatical_range}</span>
                    </div>
                  </div>
                </div>

                {/* Detailed Feedback */}
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <SparklesIcon className="h-5 w-5 mr-2 text-primary-600" />
                    Detailed Feedback
                  </h2>
                  
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result.feedback.detailed_feedback}
                    </ReactMarkdown>
                  </div>

                  {result.feedback.suggestions && result.feedback.suggestions.length > 0 && (
                    <div className="mt-6">
                      <h3 className="text-md font-semibold text-gray-900 mb-3">Suggestions for Improvement</h3>
                      <ul className="space-y-2">
                        {result.feedback.suggestions.map((suggestion, index) => (
                          <li key={index} className="flex items-start">
                            <span className="flex-shrink-0 w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3"></span>
                            <span className="text-gray-700">{suggestion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="text-center py-12">
                  <ChartBarIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Assessment Yet</h3>
                  <p className="text-gray-500">Write an essay and click "Assess Essay" to see your results here.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


