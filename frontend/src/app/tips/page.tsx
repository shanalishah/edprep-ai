'use client'

import { useEffect } from 'react'
import { useAuth } from '../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  BookOpenIcon,
  SpeakerWaveIcon,
  EyeIcon,
  PencilIcon,
  MicrophoneIcon,
  LightBulbIcon,
  ArrowRightIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

export default function TipsPage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard/home')
    }
  }, [isAuthenticated, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const tipCategories = [
    {
      id: 'listening',
      title: 'Listening Tips',
      description: 'Master IELTS Listening with expert strategies and techniques',
      icon: SpeakerWaveIcon,
      color: 'bg-blue-500',
      tips: [
        'Read questions before listening to understand what to focus on',
        'Listen for keywords and synonyms in the audio',
        'Practice with different accents and speaking speeds',
        'Use the 10-minute transfer time wisely'
      ]
    },
    {
      id: 'reading',
      title: 'Reading Tips',
      description: 'Improve your reading comprehension and speed',
      icon: BookOpenIcon,
      color: 'bg-green-500',
      tips: [
        'Skim the passage first to get the main idea',
        'Look for topic sentences in each paragraph',
        'Practice different question types regularly',
        'Manage your time - 20 minutes per passage'
      ]
    },
    {
      id: 'writing',
      title: 'Writing Tips',
      description: 'Enhance your writing skills for both Task 1 and Task 2',
      icon: PencilIcon,
      color: 'bg-purple-500',
      tips: [
        'Plan your essay before writing',
        'Use a variety of sentence structures',
        'Include relevant examples and explanations',
        'Leave time to check for grammar and spelling'
      ]
    },
    {
      id: 'speaking',
      title: 'Speaking Tips',
      description: 'Build confidence and fluency in your speaking',
      icon: MicrophoneIcon,
      color: 'bg-orange-500',
      tips: [
        'Practice speaking English daily',
        'Record yourself and listen for improvements',
        'Use a range of vocabulary and grammar',
        'Stay calm and speak naturally'
      ]
    }
  ]

  const featuredTips = [
    {
      title: 'How to Improve Your IELTS Band Score by 1.0 in 30 Days',
      category: 'General',
      readTime: '5 min read',
      excerpt: 'A comprehensive guide to boosting your IELTS score with proven strategies and daily practice routines.',
      rating: 4.8,
      votes: 1247
    },
    {
      title: 'Common IELTS Writing Mistakes and How to Avoid Them',
      category: 'Writing',
      readTime: '7 min read',
      excerpt: 'Learn about the most frequent writing errors and how to eliminate them from your essays.',
      rating: 4.6,
      votes: 892
    },
    {
      title: 'IELTS Listening: Understanding Different Accents',
      category: 'Listening',
      readTime: '4 min read',
      excerpt: 'Master listening comprehension with tips for understanding British, American, and Australian accents.',
      rating: 4.7,
      votes: 1156
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Link href="/" className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">E</span>
                </div>
                <span className="ml-3 text-2xl font-bold text-gray-900">EdPrep AI</span>
              </Link>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Link href="/test-library" className="text-gray-600 hover:text-gray-900 transition-colors">Test Library</Link>
              <Link href="/tips" className="text-blue-600 font-semibold">Tips</Link>
              <Link href="/analytics" className="text-gray-600 hover:text-gray-900 transition-colors">Analytics</Link>
            </nav>
            <div className="flex items-center space-x-4">
              <Link 
                href="/auth/login"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Log In
              </Link>
              <Link 
                href="/auth/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl font-bold text-white mb-6">
              IELTS Tips & Strategies
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto">
              Expert advice and proven strategies to help you achieve your target IELTS band score. 
              Learn from certified IELTS examiners and successful candidates.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Tip Categories */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Tips by Skill
            </h2>
            <p className="text-xl text-gray-600">
              Targeted advice for each IELTS skill to maximize your performance
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {tipCategories.map((category, index) => (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300"
              >
                <div className={`w-16 h-16 ${category.color} rounded-lg flex items-center justify-center mb-4`}>
                  <category.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{category.title}</h3>
                <p className="text-gray-600 mb-4">{category.description}</p>
                <ul className="space-y-2">
                  {category.tips.map((tip, tipIndex) => (
                    <li key={tipIndex} className="flex items-start text-sm text-gray-600">
                      <LightBulbIcon className="h-4 w-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Tips */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Featured Tips
            </h2>
            <p className="text-xl text-gray-600">
              Most popular and effective tips from our expert team
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {featuredTips.map((tip, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">
                    {tip.category}
                  </span>
                  <span className="text-sm text-gray-500">{tip.readTime}</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{tip.title}</h3>
                <p className="text-gray-600 mb-4">{tip.excerpt}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <StarIcon 
                          key={i} 
                          className={`h-4 w-4 ${i < Math.floor(tip.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                        />
                      ))}
                    </div>
                    <span className="ml-2 text-sm text-gray-600">({tip.votes} votes)</span>
                  </div>
                  <Link 
                    href="#"
                    className="inline-flex items-center text-blue-600 hover:text-blue-700 font-semibold"
                  >
                    Read More
                    <ArrowRightIcon className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Put These Tips into Practice?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Start practicing with our AI-powered IELTS tests and see immediate improvements.
            </p>
            <Link
              href="/test-library"
              className="inline-flex items-center bg-white text-gray-900 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
            >
              Start Practice Tests
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">E</span>
                </div>
                <span className="ml-3 text-2xl font-bold">EdPrep AI</span>
              </div>
              <p className="text-gray-400">
                AI-powered IELTS preparation platform helping students achieve their target scores.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Practice Tests</h3>
              <ul className="space-y-2">
                <li><Link href="/test-library/listening" className="text-gray-400 hover:text-white transition-colors">Listening Tests</Link></li>
                <li><Link href="/test-library/reading" className="text-gray-400 hover:text-white transition-colors">Reading Tests</Link></li>
                <li><Link href="/test-library/writing" className="text-gray-400 hover:text-white transition-colors">Writing Tests</Link></li>
                <li><Link href="/test-library/speaking" className="text-gray-400 hover:text-white transition-colors">Speaking Tests</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2">
                <li><Link href="/tips" className="text-gray-400 hover:text-white transition-colors">IELTS Tips</Link></li>
                <li><Link href="/analytics" className="text-gray-400 hover:text-white transition-colors">Analytics</Link></li>
                <li><Link href="/auth/login" className="text-gray-400 hover:text-white transition-colors">Login</Link></li>
                <li><Link href="/auth/register" className="text-gray-400 hover:text-white transition-colors">Sign Up</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2">
                <li><Link href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</Link></li>
                <li><Link href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-400">
              © 2025 EdPrep AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}