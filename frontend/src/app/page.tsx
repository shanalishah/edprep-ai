'use client'

import { useState, useEffect } from 'react'
import { useAuth } from './providers'
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
  CheckCircleIcon,
  UserGroupIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const [currentSlide, setCurrentSlide] = useState(0)

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        router.push('/dashboard/home')
      }
    }
  }, [isAuthenticated, loading, router])

  // Auto-rotate hero slides
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % 2)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

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

  if (isAuthenticated) {
    return null
  }

  const heroSlides = [
    {
      title: "WE TAKE YOUR IELTS SCORE HIGHER",
      subtitle: "Get ready for your 2025 IELTS exam by practicing our 100+ IELTS mock tests for FREE.",
      stats: "28,000,000+ students are using our free services.",
      cta: "START NOW",
      ctaLink: "/test-library",
      background: "bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700"
    },
    {
      title: "AI-POWERED IELTS PREPARATION",
      subtitle: "Experience the future of IELTS learning with personalized AI feedback and real-time scoring.",
      stats: "Join thousands of successful IELTS candidates worldwide.",
      cta: "TRY FREE TESTS",
      ctaLink: "/test-library",
      background: "bg-gradient-to-br from-green-600 via-teal-600 to-blue-700"
    }
  ]

  const testCategories = [
    {
      id: 'listening',
      title: 'IELTS Listening Tests',
      description: 'Practice with real audio recordings and improve your listening skills',
      icon: SpeakerWaveIcon,
      color: 'bg-blue-500',
      testCount: 25,
      href: '/test-library/listening'
    },
    {
      id: 'reading',
      title: 'IELTS Reading Tests',
      description: 'Practice with authentic reading passages and improve your comprehension skills',
      icon: BookOpenIcon,
      color: 'bg-green-500',
      testCount: 30,
      href: '/test-library/reading'
    },
    {
      id: 'writing',
      title: 'IELTS Writing Tests',
      description: 'Get AI-powered feedback on your essays and improve your writing skills',
      icon: PencilIcon,
      color: 'bg-purple-500',
      testCount: 20,
      href: '/test-library/writing'
    },
    {
      id: 'speaking',
      title: 'IELTS Speaking Tests',
      description: 'Practice speaking with AI-powered feedback and improve your fluency',
      icon: MicrophoneIcon,
      color: 'bg-orange-500',
      testCount: 15,
      href: '/test-library/speaking'
    }
  ]

  const features = [
    {
      icon: ChartBarIcon,
      title: "Real-time AI Scoring",
      description: "Get instant, accurate band scores with detailed feedback on all four IELTS skills."
    },
    {
      icon: UserGroupIcon,
      title: "Expert-Reviewed Content",
      description: "All tests are created by certified IELTS examiners and experienced teachers."
    },
    {
      icon: SparklesIcon,
      title: "Personalized Learning",
      description: "AI adapts to your learning style and provides targeted improvement suggestions."
    },
    {
      icon: ClockIcon,
      title: "Flexible Practice",
      description: "Practice anytime, anywhere with our mobile-friendly platform."
    },
    {
      icon: TrophyIcon,
      title: "Proven Results",
      description: "Students improve their band scores by 0.5-1.5 points on average."
    },
    {
      icon: AcademicCapIcon,
      title: "Comprehensive Analytics",
      description: "Track your progress with detailed analytics and performance insights."
    }
  ]

  const stats = [
    { number: "100+", label: "Practice Tests" },
    { number: "28M+", label: "Test Takers" },
    { number: "120+", label: "Countries" },
    { number: "7M+", label: "Completed Tests" }
  ]

  const testimonials = [
    {
      name: "Sarah Johnson",
      score: "Band 8.0",
      text: "EdPrep AI helped me achieve my target score in just 3 months. The AI feedback was incredibly detailed and helpful."
    },
    {
      name: "Ahmed Hassan",
      score: "Band 7.5",
      text: "The practice tests are so realistic! I felt completely prepared for my actual IELTS exam."
    },
    {
      name: "Maria Rodriguez",
      score: "Band 8.5",
      text: "The personalized learning approach made all the difference. I improved by 1.5 bands!"
    }
  ]

  return (
    <div className="min-h-screen bg-white">
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
              <Link href="/tips" className="text-gray-600 hover:text-gray-900 transition-colors">Tips</Link>
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
      <section className="relative overflow-hidden">
        <div className={`${heroSlides[currentSlide].background} min-h-screen flex items-center`}>
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
                className="text-white"
              >
                <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                  {heroSlides[currentSlide].title}
                </h1>
                <p className="text-xl mb-8 text-white/90 leading-relaxed">
                  {heroSlides[currentSlide].subtitle}
                </p>
                <div className="flex items-center mb-8">
                  <UserGroupIcon className="h-6 w-6 mr-3 text-yellow-400" />
                  <span className="text-lg text-white/90">
                    {heroSlides[currentSlide].stats}
                  </span>
                </div>
                <Link
                  href={heroSlides[currentSlide].ctaLink}
                  className="inline-flex items-center bg-white text-gray-900 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
                >
                  {heroSlides[currentSlide].cta}
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Link>
              </motion.div>
              
              <motion.div
                key={`animation-${currentSlide}`}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="relative"
              >
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                  <div className="grid grid-cols-2 gap-4">
                    {testCategories.map((category, index) => (
                      <motion.div
                        key={category.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 + index * 0.1 }}
                        className="bg-white/20 backdrop-blur-sm rounded-lg p-4 text-center"
                      >
                        <category.icon className="h-8 w-8 mx-auto mb-2 text-white" />
                        <h3 className="text-sm font-semibold text-white mb-1">{category.title}</h3>
                        <p className="text-xs text-white/80">{category.testCount} tests</p>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
          
          {/* Slide Indicators */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2">
            {heroSlides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-3 h-3 rounded-full transition-all duration-200 ${
                  index === currentSlide ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Test Categories Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Practice All IELTS Skills
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive practice tests for all four IELTS skills with AI-powered feedback and real-time scoring.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {testCategories.map((category, index) => (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
              >
                <div className={`w-16 h-16 ${category.color} rounded-lg flex items-center justify-center mb-4`}>
                  <category.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{category.title}</h3>
                <p className="text-gray-600 mb-4">{category.description}</p>
                <Link
                  href={category.href}
                  className="inline-flex items-center text-blue-600 hover:text-blue-700 font-semibold"
                >
                  Start Practice
                  <ArrowRightIcon className="ml-1 h-4 w-4" />
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose EdPrep AI?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Advanced AI technology meets expert IELTS preparation to give you the best learning experience.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center p-6"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              Trusted by Millions Worldwide
            </h2>
            <p className="text-xl text-white/90">
              Join the global community of successful IELTS candidates
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">{stat.number}</div>
                <div className="text-white/90">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              What Our Students Say
            </h2>
            <p className="text-xl text-gray-600">
              Real success stories from IELTS candidates who achieved their target scores
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold text-lg">
                      {testimonial.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div className="ml-4">
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-blue-600 font-semibold">{testimonial.score}</p>
                  </div>
                </div>
                <p className="text-gray-600 italic">"{testimonial.text}"</p>
                <div className="flex mt-4">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Ready to Achieve Your Target IELTS Score?
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of successful candidates and start your IELTS preparation journey today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/test-library"
                className="inline-flex items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              >
                <PlayIcon className="mr-2 h-5 w-5" />
                Start Free Practice
              </Link>
              <Link
                href="/auth/register"
                className="inline-flex items-center border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg font-semibold text-lg hover:border-gray-400 transition-all duration-200"
              >
                Create Account
              </Link>
            </div>
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
              © 2025 EdPrep AI. All rights reserved. IELTS is a registered trademark of University of Cambridge, the British Council, and IDP Education Australia.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}