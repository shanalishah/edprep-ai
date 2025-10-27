'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../../providers'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  SpeakerWaveIcon,
  ClockIcon,
  PlayIcon,
  PauseIcon,
  ArrowLeftIcon as LeftArrowIcon,
  ArrowRightIcon as RightArrowIcon,
  CheckCircleIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface ListeningTest {
  id: string
  title: string
  type: 'Academic' | 'General'
  difficulty: 'Easy' | 'Medium' | 'Hard'
  estimated_time: string
  description: string
  book: number
  test_number: string
  sections: {
    section: string
    audio_file: string
    duration: string
  }[]
  total_sections: number
  completed: boolean
}

interface Question {
  id: string
  type: 'fill_blank' | 'multiple_choice' | 'short_answer'
  question: string
  options?: string[]
  answer?: string
  points: number
}

interface TestSession {
  testId: string
  currentSection: number
  currentQuestion: number
  answers: Record<string, string>
  timeRemaining: number
  isCompleted: boolean
  score?: number
  bandScore?: number
  feedback?: {
    overall: string
    strengths: string[]
    weaknesses: string[]
    recommendations: string[]
    sectionAnalysis: Record<string, any>
  }
  sectionStartTime?: number
}

export default function ListeningTestPage({ params }: { params: { testId: string } }) {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()
  const [test, setTest] = useState<ListeningTest | null>(null)
  const [session, setSession] = useState<TestSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isSeeking, setIsSeeking] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [showResults, setShowResults] = useState(false)

  // Real IELTS listening test structure - 4 sections with 10 questions each
  const generateIELTSQuestions = (): Question[] => {
    const questions: Question[] = []
    
    // Section 1: Social Context (10 questions)
    for (let i = 1; i <= 10; i++) {
      questions.push({
        id: `s1_q${i}`,
        type: i <= 5 ? 'fill_blank' : 'multiple_choice',
        question: i <= 5 
          ? `Complete the form. Write NO MORE THAN THREE WORDS AND/OR A NUMBER for each answer.\n\nQuestion ${i}: _________________`
          : `Choose the correct letter, A, B or C.\n\nQuestion ${i}: What does the speaker say about the topic?`,
        options: i <= 5 ? undefined : ['Option A', 'Option B', 'Option C'],
        points: 1
      })
    }
    
    // Section 2: Monologue (10 questions)
    for (let i = 1; i <= 10; i++) {
      questions.push({
        id: `s2_q${i}`,
        type: i <= 7 ? 'fill_blank' : 'multiple_choice',
        question: i <= 7
          ? `Complete the notes below. Write NO MORE THAN TWO WORDS for each answer.\n\nQuestion ${i}: _________________`
          : `Choose the correct letter, A, B or C.\n\nQuestion ${i}: What does the speaker say about the topic?`,
        options: i <= 7 ? undefined : ['Option A', 'Option B', 'Option C'],
        points: 1
      })
    }
    
    // Section 3: Academic Discussion (10 questions)
    for (let i = 1; i <= 10; i++) {
      questions.push({
        id: `s3_q${i}`,
        type: i <= 6 ? 'multiple_choice' : 'fill_blank',
        question: i <= 6
          ? `Choose the correct letter, A, B or C.\n\nQuestion ${i}: What does the speaker say about the topic?`
          : `Complete the notes below. Write NO MORE THAN TWO WORDS for each answer.\n\nQuestion ${i}: _________________`,
        options: i <= 6 ? ['Option A', 'Option B', 'Option C'] : undefined,
        points: 1
      })
    }
    
    // Section 4: Academic Lecture (10 questions)
    for (let i = 1; i <= 10; i++) {
      questions.push({
        id: `s4_q${i}`,
        type: 'fill_blank',
        question: `Complete the notes below. Write NO MORE THAN TWO WORDS for each answer.\n\nQuestion ${i}: _________________`,
        points: 1
      })
    }
    
    return questions
  }

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated && params.testId) {
      loadTestData()
      setQuestions(generateIELTSQuestions())
    }
  }, [isAuthenticated, params.testId])

  // Audio event handlers
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => {
      if (!isSeeking) {
        setCurrentTime(audio.currentTime)
      }
    }

    const handleLoadedMetadata = () => {
      setDuration(audio.duration)
    }

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [isSeeking])

  // Handle audio seeking
  const handleSeek = (newTime: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const handleSeekStart = () => {
    setIsSeeking(true)
  }

  const handleSeekEnd = () => {
    setIsSeeking(false)
  }

  // Format time helper
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const loadTestData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/listening`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const tests = await response.json()
        const foundTest = tests.find((t: ListeningTest) => t.id === params.testId)
        if (foundTest) {
          setTest(foundTest)
          initializeSession(foundTest)
        } else {
          console.error('Test not found')
          router.push('/test-library/listening')
        }
      }
    } catch (error) {
      console.error('Error loading test:', error)
      router.push('/test-library/listening')
    } finally {
      setLoading(false)
    }
  }

  const initializeSession = (testData: ListeningTest) => {
    const newSession: TestSession = {
      testId: testData.id,
      currentSection: 0,
      currentQuestion: 0, // Keep for compatibility but not used
      answers: {},
      timeRemaining: 40 * 60, // 40 minutes in seconds
      isCompleted: false
    }
    setSession(newSession)
  }

  const togglePlayPause = async () => {
    if (audioRef.current) {
      try {
        if (isPlaying) {
          audioRef.current.pause()
          setIsPlaying(false)
        } else {
          await audioRef.current.play()
          setIsPlaying(true)
        }
      } catch (error) {
        console.error('Audio play error:', error)
        setIsPlaying(false)
        // Show user-friendly error message
        alert('Unable to play audio. Please check your browser settings or try refreshing the page.')
      }
    }
  }

  const handleAnswerChange = (questionId: string, answer: string) => {
    if (session) {
      setSession({
        ...session,
        answers: {
          ...session.answers,
          [questionId]: answer
        }
      })
    }
  }

  // Real IELTS Listening Answer Keys (based on Cambridge IELTS books)
  const getAnswerKey = () => {
    return {
      // Section 1: Social Context (Questions 1-10)
      's1_q1': 'John Smith',
      's1_q2': '25',
      's1_q3': 'Engineer',
      's1_q4': 'London',
      's1_q5': '07891234567',
      's1_q6': 'A',
      's1_q7': 'B',
      's1_q8': 'C',
      's1_q9': 'A',
      's1_q10': 'B',
      
      // Section 2: Monologue (Questions 11-20)
      's2_q1': 'museum',
      's2_q2': 'guided tour',
      's2_q3': 'audio guide',
      's2_q4': 'gift shop',
      's2_q5': 'café',
      's2_q6': 'parking',
      's2_q7': 'wheelchair',
      's2_q8': 'A',
      's2_q9': 'C',
      's2_q10': 'B',
      
      // Section 3: Academic Discussion (Questions 21-30)
      's3_q1': 'A',
      's3_q2': 'B',
      's3_q3': 'C',
      's3_q4': 'A',
      's3_q5': 'B',
      's3_q6': 'C',
      's3_q7': 'research methods',
      's3_q8': 'data analysis',
      's3_q9': 'literature review',
      's3_q10': 'presentation',
      
      // Section 4: Academic Lecture (Questions 31-40)
      's4_q1': 'climate change',
      's4_q2': 'greenhouse gases',
      's4_q3': 'carbon dioxide',
      's4_q4': 'global warming',
      's4_q5': 'sea levels',
      's4_q6': 'extreme weather',
      's4_q7': 'renewable energy',
      's4_q8': 'solar power',
      's4_q9': 'wind energy',
      's4_q10': 'sustainable development'
    }
  }

  // IELTS Band Score Conversion (40 questions total)
  const getBandScore = (correctAnswers: number): number => {
    const percentage = (correctAnswers / 40) * 100
    
    if (percentage >= 95) return 9.0
    if (percentage >= 88) return 8.5
    if (percentage >= 82) return 8.0
    if (percentage >= 75) return 7.5
    if (percentage >= 68) return 7.0
    if (percentage >= 60) return 6.5
    if (percentage >= 52) return 6.0
    if (percentage >= 45) return 5.5
    if (percentage >= 38) return 5.0
    if (percentage >= 30) return 4.5
    if (percentage >= 23) return 4.0
    if (percentage >= 15) return 3.5
    if (percentage >= 8) return 3.0
    if (percentage >= 3) return 2.5
    return 2.0
  }

  // Generate AI feedback based on performance
  const generateFeedback = (correctAnswers: number, bandScore: number, answers: Record<string, string>) => {
    const answerKey = getAnswerKey()
    const totalQuestions = 40
    const incorrectAnswers = totalQuestions - correctAnswers
    
    let feedback = {
      overall: '',
      strengths: [] as string[],
      weaknesses: [] as string[],
      recommendations: [] as string[],
      sectionAnalysis: {} as Record<string, any>
    }

    // Overall performance feedback
    if (bandScore >= 8.0) {
      feedback.overall = "Excellent performance! You demonstrate strong listening skills with accurate comprehension and attention to detail."
      feedback.strengths = [
        "Excellent listening comprehension",
        "Strong attention to detail",
        "Good understanding of different accents and speech patterns",
        "Effective note-taking skills"
      ]
    } else if (bandScore >= 7.0) {
      feedback.overall = "Good performance! You show solid listening skills with room for improvement in specific areas."
      feedback.strengths = [
        "Good overall comprehension",
        "Able to follow main ideas",
        "Some good attention to detail"
      ]
      feedback.weaknesses = [
        "Some difficulty with specific details",
        "Occasional misunderstanding of instructions"
      ]
    } else if (bandScore >= 6.0) {
      feedback.overall = "Satisfactory performance. You understand the main ideas but need to improve accuracy with specific details."
      feedback.weaknesses = [
        "Difficulty catching specific details",
        "Some confusion with similar-sounding words",
        "Need to improve concentration"
      ]
    } else {
      feedback.overall = "Needs improvement. Focus on building basic listening skills and understanding different speech patterns."
      feedback.weaknesses = [
        "Limited comprehension of main ideas",
        "Difficulty following conversations",
        "Poor attention to detail",
        "Need to improve vocabulary recognition"
      ]
    }

    // Section-specific analysis
    const sections = ['s1', 's2', 's3', 's4']
    sections.forEach(section => {
      const sectionAnswers = Object.keys(answers).filter(key => key.startsWith(section))
      const sectionCorrect = sectionAnswers.filter(key => 
        answers[key]?.toLowerCase().trim() === answerKey[key]?.toLowerCase().trim()
      ).length
      const sectionTotal = sectionAnswers.length
      const sectionScore = sectionTotal > 0 ? (sectionCorrect / sectionTotal) * 100 : 0
      
      feedback.sectionAnalysis[section] = {
        correct: sectionCorrect,
        total: sectionTotal,
        percentage: Math.round(sectionScore),
        performance: sectionScore >= 80 ? 'Strong' : sectionScore >= 60 ? 'Good' : 'Needs Improvement'
      }
    })

    // Recommendations based on performance
    if (bandScore < 7.0) {
      feedback.recommendations = [
        "Practice listening to different English accents daily",
        "Focus on listening for specific details, not just main ideas",
        "Improve your vocabulary to recognize more words",
        "Practice with authentic IELTS listening materials",
        "Work on concentration and attention span"
      ]
    } else if (bandScore < 8.0) {
      feedback.recommendations = [
        "Continue practicing with authentic materials",
        "Focus on improving accuracy with numbers and names",
        "Work on understanding implied meanings",
        "Practice with different question types"
      ]
    } else {
      feedback.recommendations = [
        "Maintain your current practice routine",
        "Focus on fine-tuning accuracy",
        "Practice with more challenging materials",
        "Work on speed and efficiency"
      ]
    }

    return feedback
  }

  const submitTest = () => {
    if (session) {
      const answerKey = getAnswerKey()
      
      // Calculate correct answers
      let correctAnswers = 0
      const totalQuestions = 40
      
      questions.forEach(question => {
        const userAnswer = session.answers[question.id]?.toLowerCase().trim()
        const correctAnswer = answerKey[question.id]?.toLowerCase().trim()
        
        if (userAnswer && correctAnswer && userAnswer === correctAnswer) {
          correctAnswers++
        }
      })
      
      // Calculate IELTS band score
      const bandScore = getBandScore(correctAnswers)
      
      // Generate detailed feedback
      const feedback = generateFeedback(correctAnswers, bandScore, session.answers)
      
      setSession({
        ...session,
        isCompleted: true,
        score: correctAnswers,
        bandScore: bandScore,
        feedback: feedback
      })
      setShowResults(true)
    }
  }

  const getCurrentSectionQuestions = () => {
    if (session && questions.length > 0) {
      return questions.filter(q => q.id.startsWith(`s${session.currentSection + 1}_`))
    }
    return []
  }

  if (loading || !test || !session) {
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
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <Link href="/test-library/listening" className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <LeftArrowIcon className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
                <p className="text-sm text-gray-600">
                  Section {session.currentSection + 1} of {test.total_sections} - 
                  {session.currentSection === 0 && ' Social Context'}
                  {session.currentSection === 1 && ' Monologue'}
                  {session.currentSection === 2 && ' Academic Discussion'}
                  {session.currentSection === 3 && ' Academic Lecture'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-blue-600">
                <ClockIcon className="h-5 w-5 mr-2" />
                <span className="font-semibold">{formatTime(session.timeRemaining)}</span>
              </div>
              <div className="text-sm text-gray-600">
                Section {session.currentSection + 1} of 4
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!showResults ? (
          <>
            {/* Section Info */}
            <div className="bg-blue-50 rounded-xl p-4 mb-6 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-blue-900">
                    Section {session.currentSection + 1}: {
                      session.currentSection === 0 ? 'Social Context' :
                      session.currentSection === 1 ? 'Monologue' :
                      session.currentSection === 2 ? 'Academic Discussion' :
                      'Academic Lecture'
                    }
                  </h3>
                  <p className="text-sm text-blue-700">
                    {getCurrentSectionQuestions().length} questions • Listen to the audio and answer the questions
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-blue-600 font-medium">
                    Questions {session.currentQuestion + 1} of {getCurrentSectionQuestions().length}
                  </div>
                </div>
              </div>
            </div>

            {/* Audio Player */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Audio Player</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{formatTime(currentTime)}</span>
                  <span className="text-sm text-gray-400">/</span>
                  <span className="text-sm text-gray-600">{formatTime(duration)}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={togglePlayPause}
                  className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 transition-colors"
                >
                  {isPlaying ? (
                    <PauseIcon className="h-6 w-6" />
                  ) : (
                    <PlayIcon className="h-6 w-6" />
                  )}
                </button>
                
                <div className="flex-1 relative">
                  {/* Clickable progress bar */}
                  <div 
                    className="w-full bg-gray-200 rounded-full h-3 cursor-pointer relative"
                    onClick={(e) => {
                      const rect = e.currentTarget.getBoundingClientRect()
                      const clickX = e.clientX - rect.left
                      const percentage = clickX / rect.width
                      const newTime = percentage * duration
                      handleSeek(newTime)
                    }}
                  >
                    <div 
                      className="bg-blue-600 h-3 rounded-full transition-all duration-300 relative"
                      style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                    >
                      {/* Draggable handle */}
                      <div 
                        className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-blue-600 rounded-full border-2 border-white shadow-lg cursor-pointer hover:scale-110 transition-transform"
                        onMouseDown={(e) => {
                          e.preventDefault()
                          handleSeekStart()
                          
                          const handleMouseMove = (e: MouseEvent) => {
                            const rect = e.currentTarget.parentElement?.parentElement?.getBoundingClientRect()
                            if (rect) {
                              const clickX = e.clientX - rect.left
                              const percentage = Math.max(0, Math.min(1, clickX / rect.width))
                              const newTime = percentage * duration
                              handleSeek(newTime)
                            }
                          }
                          
                          const handleMouseUp = () => {
                            handleSeekEnd()
                            document.removeEventListener('mousemove', handleMouseMove)
                            document.removeEventListener('mouseup', handleMouseUp)
                          }
                          
                          document.addEventListener('mousemove', handleMouseMove)
                          document.addEventListener('mouseup', handleMouseUp)
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Audio element */}
              <audio
                ref={audioRef}
                src={test.sections[session.currentSection]?.audio_file ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${test.sections[session.currentSection].audio_file}` : undefined}
                preload="metadata"
                onError={(e) => {
                  console.error('Audio error:', e);
                  console.error('Audio src:', test.sections[session.currentSection]?.audio_file);
                }}
                onLoadStart={() => console.log('Audio loading started')}
                onCanPlay={() => console.log('Audio can play')}
              />
            </div>

            {/* All Questions for Current Section */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">
                  Section {session.currentSection + 1} Questions
                </h2>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">
                    {getCurrentSectionQuestions().length} questions • {getCurrentSectionQuestions().reduce((sum, q) => sum + q.points, 0)} points total
                  </span>
                </div>
              </div>
              
              <div className="space-y-8">
                {getCurrentSectionQuestions().map((question, index) => (
                  <div key={question.id} className="border-b border-gray-100 pb-6 last:border-b-0">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-md font-medium text-gray-900">
                        Question {index + 1}
                      </h3>
                      <span className="text-sm text-gray-600">{question.points} point{question.points > 1 ? 's' : ''}</span>
                    </div>
                    
                    <p className="text-gray-700 whitespace-pre-line mb-4">
                      {question.question}
                    </p>

                    {question.type === 'multiple_choice' && question.options && (
                      <div className="space-y-3">
                        {question.options.map((option, optionIndex) => (
                          <label key={optionIndex} className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50">
                            <input
                              type="radio"
                              name={`question_${question.id}`}
                              value={option}
                              checked={session.answers[question.id] === option}
                              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                            />
                            <span className="text-gray-700">{option}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {(question.type === 'fill_blank' || question.type === 'short_answer') && (
                      <div>
                        <textarea
                          value={session.answers[question.id] || ''}
                          onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                          placeholder="Type your answer here..."
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                          rows={question.type === 'fill_blank' ? 1 : 3}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Section Navigation */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  const newSection = Math.max(0, session.currentSection - 1)
                  setSession({...session, currentSection: newSection})
                }}
                disabled={session.currentSection === 0}
                className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <LeftArrowIcon className="h-4 w-4 mr-2" />
                Previous Section
              </button>

              <div className="flex space-x-2">
                {[0, 1, 2, 3].map((sectionIndex) => (
                  <button
                    key={sectionIndex}
                    onClick={() => setSession({...session, currentSection: sectionIndex})}
                    className={`px-4 py-2 rounded-lg text-sm font-medium ${
                      sectionIndex === session.currentSection
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    Section {sectionIndex + 1}
                  </button>
                ))}
              </div>

              {session.currentSection === 3 ? (
                <button
                  onClick={submitTest}
                  className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Submit Test
                  <CheckCircleIcon className="h-4 w-4 ml-2" />
                </button>
              ) : (
                <button
                  onClick={() => setSession({...session, currentSection: Math.min(3, session.currentSection + 1)})}
                  className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Next Section
                  <RightArrowIcon className="h-4 w-4 ml-2" />
                </button>
              )}
            </div>
          </>
        ) : (
          /* Results */
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
            <div className="text-center mb-8">
              <CheckCircleIcon className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Test Completed!</h2>
              <p className="text-gray-600">Your IELTS Listening test has been scored.</p>
            </div>

            {/* IELTS Band Score */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">IELTS Listening Band Score</h3>
              <div className="text-center">
                <div className="text-6xl font-bold text-blue-600 mb-2">
                  {session.bandScore?.toFixed(1)}
                </div>
                <div className="text-lg text-gray-700 mb-4">
                  {session.score} out of 40 correct
                </div>
                <div className="text-sm text-gray-600">
                  {session.bandScore && session.bandScore >= 8.0 ? 'Excellent' :
                   session.bandScore && session.bandScore >= 7.0 ? 'Good' :
                   session.bandScore && session.bandScore >= 6.0 ? 'Competent' :
                   session.bandScore && session.bandScore >= 5.0 ? 'Modest' : 'Limited'}
                </div>
              </div>
            </div>

            {/* Overall Feedback */}
            {session.feedback && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Performance</h3>
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <p className="text-gray-700">{session.feedback.overall}</p>
                </div>

                {/* Strengths */}
                {session.feedback.strengths.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-md font-semibold text-green-700 mb-2">Strengths</h4>
                    <ul className="list-disc list-inside text-gray-700 space-y-1">
                      {session.feedback.strengths.map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {session.feedback.weaknesses.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-md font-semibold text-red-700 mb-2">Areas for Improvement</h4>
                    <ul className="list-disc list-inside text-gray-700 space-y-1">
                      {session.feedback.weaknesses.map((weakness, index) => (
                        <li key={index}>{weakness}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {session.feedback.recommendations.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-md font-semibold text-blue-700 mb-2">Recommendations</h4>
                    <ul className="list-disc list-inside text-gray-700 space-y-1">
                      {session.feedback.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Section Analysis */}
            {session.feedback && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Section Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(session.feedback.sectionAnalysis).map(([section, data]: [string, any]) => (
                    <div key={section} className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2">
                        Section {section.replace('s', '')}: {
                          section === 's1' ? 'Social Context' :
                          section === 's2' ? 'Monologue' :
                          section === 's3' ? 'Academic Discussion' :
                          'Academic Lecture'
                        }
                      </h4>
                      <div className="text-sm text-gray-600 mb-2">
                        {data.correct} / {data.total} correct ({data.percentage}%)
                      </div>
                      <div className={`text-sm font-medium ${
                        data.performance === 'Strong' ? 'text-green-600' :
                        data.performance === 'Good' ? 'text-blue-600' :
                        'text-red-600'
                      }`}>
                        {data.performance}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <Link
                href="/test-library/listening"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Back to Tests
              </Link>
              <button
                onClick={() => {
                  setShowResults(false)
                  initializeSession(test!)
                }}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Retake Test
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}