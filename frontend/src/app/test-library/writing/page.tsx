'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  PencilIcon,
  ClockIcon,
  StarIcon,
  ChartBarIcon,
  PlayIcon,
  BookOpenIcon,
  AcademicCapIcon,
  TrophyIcon,
  ArrowLeftIcon,
  EyeIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface WritingTest {
  id: number
  title: string
  taskType: 'Task 1' | 'Task 2'
  topic: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  estimatedTime: string
  wordCount: number
  description: string
  prompt: string
  sampleAnswer?: string
  bandScore?: number
  completed: boolean
}

export default function WritingTestsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [tests, setTests] = useState<WritingTest[]>([])
  const [filter, setFilter] = useState<'all' | 'Task 1' | 'Task 2'>('all')
  const [difficulty, setDifficulty] = useState<'all' | 'Easy' | 'Medium' | 'Hard'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      loadWritingTests()
    }
  }, [isAuthenticated])

  const loadWritingTests = async () => {
    // Mock data - in real implementation, this would come from API
    const mockTests: WritingTest[] = [
      {
        id: 1,
        title: "Technology and Communication",
        taskType: "Task 2",
        topic: "Technology",
        difficulty: "Medium",
        estimatedTime: "40 min",
        wordCount: 250,
        description: "Discuss the impact of technology on modern communication",
        prompt: "Some people believe that technology has made our lives more complicated, while others think it has made life easier. Discuss both views and give your opinion.",
        completed: false
      },
      {
        id: 2,
        title: "Education and Experience",
        taskType: "Task 2",
        topic: "Education",
        difficulty: "Easy",
        estimatedTime: "35 min",
        wordCount: 250,
        description: "Compare the importance of education vs experience",
        prompt: "Some people think that formal education is more important than practical experience. Others believe that practical experience is more valuable. Discuss both views and give your opinion.",
        completed: true,
        bandScore: 7.5
      },
      {
        id: 3,
        title: "Environmental Protection",
        taskType: "Task 2",
        topic: "Environment",
        difficulty: "Hard",
        estimatedTime: "45 min",
        wordCount: 250,
        description: "Analyze environmental challenges and solutions",
        prompt: "Environmental problems are becoming increasingly serious. What are the main causes of these problems? What measures can be taken to address them?",
        completed: false
      },
      {
        id: 4,
        title: "Bar Chart - Energy Consumption",
        taskType: "Task 1",
        topic: "Data Analysis",
        difficulty: "Medium",
        estimatedTime: "20 min",
        wordCount: 150,
        description: "Describe energy consumption patterns in different countries",
        prompt: "The chart below shows the energy consumption in different countries from 2000 to 2010. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
        completed: false
      },
      {
        id: 5,
        title: "Work-Life Balance",
        taskType: "Task 2",
        topic: "Work",
        difficulty: "Medium",
        estimatedTime: "40 min",
        wordCount: 250,
        description: "Discuss modern work-life balance challenges",
        prompt: "In many countries, people are working longer hours than ever before. What are the causes of this trend? What effects does it have on individuals and society?",
        completed: true,
        bandScore: 6.5
      },
      {
        id: 6,
        title: "Line Graph - Population Growth",
        taskType: "Task 1",
        topic: "Data Analysis",
        difficulty: "Easy",
        estimatedTime: "20 min",
        wordCount: 150,
        description: "Describe population growth trends over time",
        prompt: "The line graph below shows the population growth in three different cities from 1990 to 2010. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
        completed: false
      }
    ]
    
    setTests(mockTests)
    setLoading(false)
  }

  const filteredTests = tests.filter(test => {
    const matchesFilter = filter === 'all' || test.taskType === filter
    const matchesDifficulty = difficulty === 'all' || test.difficulty === difficulty
    return matchesFilter && matchesDifficulty
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTaskTypeColor = (taskType: string) => {
    switch (taskType) {
      case 'Task 1': return 'bg-blue-100 text-blue-800'
      case 'Task 2': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <Link href="/test-library" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <ArrowLeftIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">IELTS Writing Tests</h1>
                <p className="text-gray-600 mt-1">Practice Task 1 and Task 2 with AI-powered feedback</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Tests: {tests.length}</p>
              <p className="text-lg font-semibold text-primary-600">
                Completed: {tests.filter(t => t.completed).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-200">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Tasks</option>
                <option value="Task 1">Task 1 (Academic/General)</option>
                <option value="Task 2">Task 2 (Essay)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Levels</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tests Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTests.map((test, index) => (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:border-primary-300 transition-all duration-200"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTaskTypeColor(test.taskType)}`}>
                    {test.taskType}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                    {test.difficulty}
                  </span>
                </div>
                {test.completed && (
                  <div className="flex items-center text-green-600">
                    <TrophyIcon className="h-5 w-5 mr-1" />
                    <span className="text-sm font-semibold">{test.bandScore}</span>
                  </div>
                )}
              </div>

              {/* Title and Description */}
              <h3 className="text-lg font-bold text-gray-900 mb-2">{test.title}</h3>
              <p className="text-gray-600 text-sm mb-4">{test.description}</p>

              {/* Prompt Preview */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <p className="text-sm text-gray-700 line-clamp-3">{test.prompt}</p>
              </div>

              {/* Test Info */}
              <div className="space-y-2 text-sm text-gray-500 mb-4">
                <div className="flex items-center justify-between">
                  <span>Estimated Time:</span>
                  <span className="font-semibold">{test.estimatedTime}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Word Count:</span>
                  <span className="font-semibold">{test.wordCount} words</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Topic:</span>
                  <span className="font-semibold">{test.topic}</span>
                </div>
              </div>

              {/* Action Button */}
              <Link href={`/test-library/writing/${test.id}`}>
                <button className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center ${
                  test.completed 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-primary-600 text-white hover:bg-primary-700'
                }`}>
                  {test.completed ? (
                    <>
                      <EyeIcon className="h-5 w-5 mr-2" />
                      Review Test
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Test
                    </>
                  )}
                </button>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTests.length === 0 && (
          <div className="text-center py-12">
            <BookOpenIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No tests found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more tests.</p>
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-12 bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl p-8 border border-primary-200">
          <h2 className="text-2xl font-bold text-primary-900 mb-6 text-center">💡 Writing Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <SparklesIcon className="h-5 w-5 text-primary-600 mr-2" />
                Task 1 Tips
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• Spend 20 minutes maximum on Task 1</li>
                <li>• Write at least 150 words</li>
                <li>• Focus on key trends and comparisons</li>
                <li>• Use appropriate vocabulary for data description</li>
                <li>• Organize information logically</li>
              </ul>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <AcademicCapIcon className="h-5 w-5 text-primary-600 mr-2" />
                Task 2 Tips
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li>• Spend 40 minutes on Task 2</li>
                <li>• Write at least 250 words</li>
                <li>• Plan your essay before writing</li>
                <li>• Address all parts of the question</li>
                <li>• Use examples to support your arguments</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
