'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  BookOpenIcon,
  ClockIcon,
  ArrowLeftIcon as LeftArrowIcon,
  ArrowRightIcon as RightArrowIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ReadingTest {
  id: string
  title: string
  type: 'Academic' | 'General Training'
  difficulty: 'Easy' | 'Medium' | 'Hard'
  estimated_time: string
  description: string
  book: number
  pdf_file: string
  total_passages: number
  total_questions: number
}

interface ReadingPassage {
  id: string
  title: string
  content: string
  questions: ReadingQuestion[]
}

interface ReadingQuestion {
  id: string
  number: number
  type: 'multiple_choice' | 'true_false_not_given' | 'fill_in_blank' | 'matching' | 'short_answer'
  question: string
  options?: string[]
  correct_answer: string
  points: number
}

interface TestSession {
  testId: string
  startTime: Date
  timeRemaining: number
  currentPassage: number
  answers: { [questionId: string]: string }
  isCompleted: boolean
  score?: number
}

export default function ReadingTestPage({ params }: { params: { testId: string } }) {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [test, setTest] = useState<ReadingTest | null>(null)
  const [passages, setPassages] = useState<ReadingPassage[]>([])
  const [session, setSession] = useState<TestSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRemaining, setTimeRemaining] = useState(3600) // 60 minutes in seconds
  const [showResults, setShowResults] = useState(false)

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

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/reading`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const tests = await response.json()
        const currentTest = tests.find((t: ReadingTest) => t.id === params.testId)
        
        if (currentTest) {
          setTest(currentTest)
          initializeSession(currentTest)
          generateReadingPassages(currentTest)
        }
      }
    } catch (error) {
      console.error('Error loading test data:', error)
    } finally {
      setLoading(false)
    }
  }

  const initializeSession = (testData: ReadingTest) => {
    const newSession: TestSession = {
      testId: testData.id,
      startTime: new Date(),
      timeRemaining: 3600, // 60 minutes
      currentPassage: 0,
      answers: {},
      isCompleted: false
    }
    setSession(newSession)
    setTimeRemaining(3600)
  }

  const generateReadingPassages = (testData: ReadingTest) => {
    // Generate realistic IELTS reading passages and questions
    const generatedPassages: ReadingPassage[] = [
      {
        id: 'passage_1',
        title: 'The History of Renewable Energy',
        content: `The development of renewable energy sources has been one of the most significant technological advances of the 21st century. Solar power, wind energy, and hydroelectric power have transformed the global energy landscape, offering sustainable alternatives to fossil fuels.

The concept of harnessing solar energy dates back to ancient civilizations, but it wasn't until the 1950s that practical solar panels were developed. The space race accelerated solar technology development, as spacecraft required reliable power sources. Today, solar panels are increasingly affordable and efficient, making solar power accessible to millions of households worldwide.

Wind energy has an even longer history, with windmills being used for centuries to grind grain and pump water. Modern wind turbines represent a sophisticated evolution of this ancient technology. Offshore wind farms, in particular, have become increasingly popular due to their ability to generate large amounts of electricity without occupying valuable land.

Hydropower remains the most established form of renewable energy, with hydroelectric dams providing clean electricity for over a century. While large-scale dams can have environmental impacts, smaller run-of-river projects offer more sustainable alternatives.

The integration of renewable energy sources into national grids presents both opportunities and challenges. Smart grid technology enables better management of variable renewable energy sources, while energy storage systems help address the intermittent nature of solar and wind power.

Despite these advances, renewable energy still faces obstacles including high initial costs, regulatory barriers, and resistance from established fossil fuel industries. However, as technology continues to improve and costs decrease, renewable energy is becoming increasingly competitive with traditional energy sources.`,
        questions: [
          {
            id: 'q1',
            number: 1,
            type: 'multiple_choice',
            question: 'According to the passage, when were practical solar panels first developed?',
            options: ['Ancient times', '1950s', '21st century', 'During the space race'],
            correct_answer: '1950s',
            points: 1
          },
          {
            id: 'q2',
            number: 2,
            type: 'true_false_not_given',
            question: 'Wind energy has been used for centuries.',
            correct_answer: 'True',
            points: 1
          },
          {
            id: 'q3',
            number: 3,
            type: 'fill_in_blank',
            question: 'Offshore wind farms are popular because they can generate electricity without occupying valuable ______.',
            correct_answer: 'land',
            points: 1
          },
          {
            id: 'q4',
            number: 4,
            type: 'multiple_choice',
            question: 'What technology helps manage variable renewable energy sources?',
            options: ['Solar panels', 'Wind turbines', 'Smart grid technology', 'Energy storage'],
            correct_answer: 'Smart grid technology',
            points: 1
          },
          {
            id: 'q5',
            number: 5,
            type: 'true_false_not_given',
            question: 'All renewable energy sources are completely reliable.',
            correct_answer: 'False',
            points: 1
          }
        ]
      },
      {
        id: 'passage_2',
        title: 'Urban Planning and Sustainable Development',
        content: `Urban planning has evolved significantly over the past century, moving from simple zoning regulations to comprehensive approaches that consider environmental, social, and economic factors. Modern urban planning emphasizes sustainable development, aiming to create cities that can meet current needs without compromising future generations' ability to meet their own needs.

The concept of sustainable urban development encompasses several key principles. Environmental sustainability focuses on reducing pollution, conserving natural resources, and protecting ecosystems. This includes promoting green building practices, developing efficient public transportation systems, and creating green spaces that improve air quality and provide recreational opportunities.

Social sustainability addresses issues of equity and inclusion, ensuring that urban development benefits all residents regardless of their socioeconomic status. This involves providing affordable housing, accessible public services, and opportunities for community participation in planning decisions.

Economic sustainability ensures that urban development supports long-term economic growth while maintaining fiscal responsibility. This includes attracting businesses, creating employment opportunities, and investing in infrastructure that supports economic activity.

Smart city technologies are increasingly being integrated into urban planning strategies. These technologies use data and digital infrastructure to improve city services, reduce resource consumption, and enhance quality of life. Examples include intelligent traffic management systems, smart energy grids, and digital platforms for citizen engagement.

However, implementing sustainable urban development faces numerous challenges. Rapid urbanization, particularly in developing countries, often outpaces planning capacity. Limited financial resources, competing priorities, and resistance to change can also hinder progress. Additionally, the complexity of urban systems requires coordination among multiple stakeholders, including government agencies, private developers, and community organizations.

Despite these challenges, many cities worldwide are successfully implementing sustainable development strategies. These cities serve as models for others, demonstrating that sustainable urban development is not only possible but also beneficial for residents, businesses, and the environment.`,
        questions: [
          {
            id: 'q6',
            number: 6,
            type: 'multiple_choice',
            question: 'What is the main goal of sustainable urban development?',
            options: ['Maximize profits', 'Meet current needs without compromising future generations', 'Reduce population growth', 'Eliminate all pollution'],
            correct_answer: 'Meet current needs without compromising future generations',
            points: 1
          },
          {
            id: 'q7',
            number: 7,
            type: 'true_false_not_given',
            question: 'Smart city technologies always reduce resource consumption.',
            correct_answer: 'Not Given',
            points: 1
          },
          {
            id: 'q8',
            number: 8,
            type: 'fill_in_blank',
            question: 'Social sustainability ensures that urban development benefits all residents regardless of their ______ status.',
            correct_answer: 'socioeconomic',
            points: 1
          },
          {
            id: 'q9',
            number: 9,
            type: 'multiple_choice',
            question: 'What is mentioned as a challenge to sustainable urban development?',
            options: ['Too much funding', 'Lack of technology', 'Rapid urbanization', 'Too many green spaces'],
            correct_answer: 'Rapid urbanization',
            points: 1
          },
          {
            id: 'q10',
            number: 10,
            type: 'true_false_not_given',
            question: 'All cities worldwide have successfully implemented sustainable development.',
            correct_answer: 'False',
            points: 1
          }
        ]
      },
      {
        id: 'passage_3',
        title: 'The Psychology of Decision Making',
        content: `Human decision-making is a complex process influenced by numerous psychological, social, and environmental factors. Understanding how people make decisions has important implications for fields ranging from economics and marketing to public policy and healthcare.

Traditional economic theory assumes that people are rational decision-makers who carefully weigh all available information to maximize their utility. However, research in behavioral economics and psychology has revealed that human decision-making is often far from rational. People frequently rely on mental shortcuts, or heuristics, that can lead to systematic biases and errors.

One of the most well-known cognitive biases is the availability heuristic, where people judge the probability of events based on how easily examples come to mind. This can lead to overestimating the likelihood of dramatic but rare events, such as plane crashes, while underestimating more common risks, such as car accidents.

Another important bias is the anchoring effect, where people\'s judgments are influenced by irrelevant information presented before making a decision. For example, real estate prices can be influenced by asking prices that are completely unrelated to the property\'s actual value.

Confirmation bias leads people to seek out information that confirms their existing beliefs while ignoring contradictory evidence. This bias can be particularly problematic in scientific research, where researchers might unconsciously favor results that support their hypotheses.

Social factors also play a crucial role in decision-making. People are influenced by what others think and do, often conforming to group norms even when they disagree with them. This social influence can be positive, encouraging pro-social behavior, or negative, leading to harmful group decisions.

Emotional states significantly affect decision-making processes. People in positive moods tend to be more optimistic and take more risks, while those in negative moods are more cautious and risk-averse. Stress can impair decision-making abilities, leading to poor choices under pressure.

Understanding these biases and influences is crucial for improving decision-making processes. Techniques such as structured decision-making frameworks, diverse perspectives, and awareness of cognitive biases can help individuals and organizations make better choices.`,
        questions: [
          {
            id: 'q11',
            number: 11,
            type: 'multiple_choice',
            question: 'What does traditional economic theory assume about human decision-making?',
            options: ['People are irrational', 'People are rational and maximize utility', 'People always make mistakes', 'People are influenced by emotions'],
            correct_answer: 'People are rational and maximize utility',
            points: 1
          },
          {
            id: 'q12',
            number: 12,
            type: 'true_false_not_given',
            question: 'The availability heuristic always leads to accurate probability judgments.',
            correct_answer: 'False',
            points: 1
          },
          {
            id: 'q13',
            number: 13,
            type: 'fill_in_blank',
            question: 'The anchoring effect occurs when people\'s judgments are influenced by ______ information.',
            correct_answer: 'irrelevant',
            points: 1
          },
          {
            id: 'q14',
            number: 14,
            type: 'multiple_choice',
            question: 'What can help improve decision-making processes?',
            options: ['Ignoring emotions', 'Avoiding group input', 'Using structured frameworks', 'Making quick decisions'],
            correct_answer: 'Using structured frameworks',
            points: 1
          },
          {
            id: 'q15',
            number: 15,
            type: 'true_false_not_given',
            question: 'Stress always improves decision-making abilities.',
            correct_answer: 'False',
            points: 1
          }
        ]
      }
    ]

    setPassages(generatedPassages)
  }

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleAnswerChange = (questionId: string, answer: string) => {
    if (!session) return
    
    setSession(prev => prev ? {
      ...prev,
      answers: {
        ...prev.answers,
        [questionId]: answer
      }
    } : null)
  }

  const handleNextPassage = () => {
    if (!session) return
    
    setSession(prev => prev ? {
      ...prev,
      currentPassage: Math.min(prev.currentPassage + 1, passages.length - 1)
    } : null)
  }

  const handlePreviousPassage = () => {
    if (!session) return
    
    setSession(prev => prev ? {
      ...prev,
      currentPassage: Math.max(prev.currentPassage - 1, 0)
    } : null)
  }

  const handleCompleteTest = async () => {
    if (!session || !test) return

    // Calculate score
    let totalScore = 0
    let totalQuestions = 0

    passages.forEach(passage => {
      passage.questions.forEach(question => {
        totalQuestions++
        const userAnswer = session.answers[question.id]
        if (userAnswer && userAnswer.toLowerCase().trim() === question.correct_answer.toLowerCase().trim()) {
          totalScore += question.points
        }
      })
    })

    const percentage = (totalScore / totalQuestions) * 100
    const bandScore = Math.min(9, Math.max(1, Math.round(percentage / 10 * 2) / 2))

    const completedSession: TestSession = {
      ...session,
      isCompleted: true,
      score: bandScore
    }

    setSession(completedSession)
    setShowResults(true)

    // Save results to backend
    try {
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
            testType: 'reading',
            score: bandScore,
            answers: session.answers,
            timeSpent: 3600 - timeRemaining
          })
        })
      }
    } catch (error) {
      console.error('Error saving test results:', error)
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
          <BookOpenIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Test not found</h3>
          <p className="text-gray-600">The reading test you\'re looking for doesn\'t exist.</p>
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
                <Link href="/test-library/reading" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                  <LeftArrowIcon className="h-6 w-6" />
                </Link>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Test Results</h1>
                  <p className="text-gray-600">{test.title}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">
                  Band Score: {session.score?.toFixed(1)}
                </div>
                <p className="text-sm text-gray-500">
                  {Math.round((Object.keys(session.answers).length / 15) * 100)}% Complete
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
              <p className="text-gray-600">You have successfully completed the reading test.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{session.score?.toFixed(1)}</div>
                <div className="text-sm text-blue-800">Band Score</div>
              </div>
              <div className="bg-green-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{Object.keys(session.answers).length}</div>
                <div className="text-sm text-green-800">Questions Answered</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">{formatTime(3600 - timeRemaining)}</div>
                <div className="text-sm text-purple-800">Time Taken</div>
              </div>
            </div>

            <div className="flex justify-center space-x-4">
              <Link href="/test-library/reading">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Back to Reading Tests
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

  const currentPassage = passages[session.currentPassage]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <Link href="/test-library/reading" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <LeftArrowIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
                <p className="text-sm text-gray-600">
                  Passage {session.currentPassage + 1} of {passages.length}
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Reading Passage */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">{currentPassage?.title}</h2>
              <DocumentTextIcon className="h-6 w-6 text-gray-400" />
            </div>
            <div className="prose max-w-none">
              <div className="text-gray-800 leading-relaxed whitespace-pre-line">
                {currentPassage?.content}
              </div>
            </div>
          </div>

          {/* Questions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900">Questions</h3>
              <span className="text-sm text-gray-500">
                {currentPassage?.questions.length} questions
              </span>
            </div>
            
            <div className="space-y-6">
              {currentPassage?.questions.map((question) => (
                <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                      Question {question.number}
                    </span>
                    <span className="text-xs text-gray-500">{question.points} point{question.points > 1 ? 's' : ''}</span>
                  </div>
                  
                  <p className="text-gray-900 mb-3 font-medium">{question.question}</p>
                  
                  {question.type === 'multiple_choice' && question.options && (
                    <div className="space-y-2">
                      {question.options.map((option, index) => (
                        <label key={index} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={session.answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-gray-700">{option}</span>
                        </label>
                      ))}
                    </div>
                  )}
                  
                  {question.type === 'true_false_not_given' && (
                    <div className="space-y-2">
                      {['True', 'False', 'Not Given'].map((option) => (
                        <label key={option} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={session.answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-gray-700">{option}</span>
                        </label>
                      ))}
                    </div>
                  )}
                  
                  {(question.type === 'fill_in_blank' || question.type === 'short_answer') && (
                    <input
                      type="text"
                      value={session.answers[question.id] || ''}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Your answer..."
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8">
          <button
            onClick={handlePreviousPassage}
            disabled={session.currentPassage === 0}
            className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <LeftArrowIcon className="h-4 w-4 mr-2" />
            Previous Passage
          </button>
          
          <div className="flex items-center space-x-2">
            {passages.map((_, index) => (
              <button
                key={index}
                onClick={() => setSession(prev => prev ? { ...prev, currentPassage: index } : null)}
                className={`w-8 h-8 rounded-full text-sm font-medium ${
                  index === session.currentPassage
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          
          {session.currentPassage === passages.length - 1 ? (
            <button
              onClick={handleCompleteTest}
              className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <CheckCircleIcon className="h-4 w-4 mr-2" />
              Complete Test
            </button>
          ) : (
            <button
              onClick={handleNextPassage}
              className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Next Passage
              <RightArrowIcon className="h-4 w-4 ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
