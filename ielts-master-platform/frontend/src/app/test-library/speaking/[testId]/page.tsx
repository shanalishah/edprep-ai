'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  PauseIcon,
  ArrowLeftIcon as LeftArrowIcon,
  ArrowRightIcon as RightArrowIcon,
  ClockIcon,
  SpeakerWaveIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../../../providers'

interface SpeakingTest {
  id: string
  title: string
  type: string
  difficulty: string
  estimated_time: string
  description: string
  topic: string
  questions: Array<{
    instruction: string
    response?: string
  }>
  total_questions: number
}

interface SpeakingSession {
  testId: string
  currentQuestion: number
  answers: Array<{
    questionIndex: number
    instruction: string
    response: string
    audioUrl?: string
    transcript?: string
    score?: number
    feedback?: string
  }>
  timeRemaining: number
  isCompleted: boolean
  isRecording: boolean
  currentTranscript: string
}

export default function SpeakingTestPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const testId = params.testId as string

  const [test, setTest] = useState<SpeakingTest | null>(null)
  const [session, setSession] = useState<SpeakingSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [assessmentResult, setAssessmentResult] = useState<any>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        setCurrentTranscript(finalTranscript + interimTranscript)
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
      }
    }
  }, [])

  const loadTestData = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/test-library/speaking`, {
        headers: {
          'Authorization': `Bearer ${user?.token || 'guest-token'}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch speaking tests')
      }

      const tests: SpeakingTest[] = await response.json()
      const foundTest = tests.find(t => t.id === testId)
      
      if (!foundTest) {
        throw new Error('Speaking test not found')
      }

      setTest(foundTest)
      initializeSession(foundTest)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load test')
    } finally {
      setIsLoading(false)
    }
  }

  const initializeSession = (testData: SpeakingTest) => {
    const newSession: SpeakingSession = {
      testId: testData.id,
      currentQuestion: 0,
      answers: [],
      timeRemaining: 15 * 60, // 15 minutes for speaking test
      isCompleted: false,
      isRecording: false,
      currentTranscript: ''
    }
    setSession(newSession)
  }

  useEffect(() => {
    if (testId) {
      loadTestData()
    }
  }, [testId])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        if (session) {
          const updatedAnswers = [...session.answers]
          const currentAnswer = updatedAnswers.find(a => a.questionIndex === session.currentQuestion)
          
          if (currentAnswer) {
            currentAnswer.audioUrl = audioUrl
            currentAnswer.transcript = currentTranscript
          } else {
            updatedAnswers.push({
              questionIndex: session.currentQuestion,
              instruction: test?.questions[session.currentQuestion]?.instruction || '',
              response: currentTranscript,
              audioUrl: audioUrl,
              transcript: currentTranscript
            })
          }

          setSession({
            ...session,
            answers: updatedAnswers,
            isRecording: false
          })
        }

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setCurrentTranscript('')

      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start()
      }
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }

  const playRecording = () => {
    if (session && session.answers[session.currentQuestion]?.audioUrl) {
      const audioUrl = session.answers[session.currentQuestion].audioUrl
      if (audioRef.current) {
        audioRef.current.src = audioUrl
        audioRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const pauseRecording = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      setIsPlaying(false)
    }
  }

  const nextQuestion = () => {
    if (session && session.currentQuestion < (test?.questions.length || 0) - 1) {
      setSession({
        ...session,
        currentQuestion: session.currentQuestion + 1,
        currentTranscript: ''
      })
    }
  }

  const previousQuestion = () => {
    if (session && session.currentQuestion > 0) {
      setSession({
        ...session,
        currentQuestion: session.currentQuestion - 1,
        currentTranscript: ''
      })
    }
  }

  const submitTest = async () => {
    if (!session || !test) return

    try {
      // Prepare responses for assessment
      const responses: { [key: string]: string } = {}
      session.answers.forEach((answer, index) => {
        responses[`question_${index}`] = answer.transcript || answer.response || ''
      })

      // Submit all answers for final assessment
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/v1/speaking/final-assessment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token || 'guest-token'}`
        },
        body: JSON.stringify({
          testId: test.id,
          responses: responses,
          timeSpent: (15 * 60) - session.timeRemaining // Calculate time spent
        })
      })

      if (!response.ok) {
        throw new Error('Failed to submit speaking test')
      }

      const result = await response.json()
      setAssessmentResult(result)
      
      setSession({
        ...session,
        isCompleted: true
      })
    } catch (error) {
      console.error('Error submitting test:', error)
      alert('Failed to submit test. Please try again.')
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading speaking test...</p>
        </div>
      </div>
    )
  }

  if (error || !test || !session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Test Not Found</h1>
          <p className="text-gray-600 mb-4">The speaking test you're looking for doesn't exist.</p>
          <button
            onClick={() => router.push('/test-library/speaking')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Speaking Tests
          </button>
        </div>
      </div>
    )
  }

  const currentQuestion = test.questions[session.currentQuestion]
  const currentAnswer = session.answers.find(a => a.questionIndex === session.currentQuestion)
  const isLastQuestion = session.currentQuestion === test.questions.length - 1

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/test-library/speaking')}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <LeftArrowIcon className="h-5 w-5 mr-2" />
                Back to Speaking Tests
              </button>
              <div className="h-6 w-px bg-gray-300" />
              <h1 className="text-lg font-semibold text-gray-900">{test.title}</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-gray-600">
                <ClockIcon className="h-4 w-4 mr-1" />
                {formatTime(session.timeRemaining)}
              </div>
              <div className="text-sm text-gray-600">
                Question {session.currentQuestion + 1} of {test.questions.length}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Question */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Question {session.currentQuestion + 1}</h2>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-800 font-medium">{currentQuestion.instruction}</p>
              </div>
            </div>

            {/* Recording Controls */}
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <MicrophoneIcon className="h-5 w-5 mr-2" />
                    Start Recording
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <StopIcon className="h-5 w-5 mr-2" />
                    Stop Recording
                  </button>
                )}
              </div>

              {/* Audio Playback */}
              {currentAnswer?.audioUrl && (
                <div className="flex items-center justify-center space-x-4">
                  {!isPlaying ? (
                    <button
                      onClick={playRecording}
                      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Play Recording
                    </button>
                  ) : (
                    <button
                      onClick={pauseRecording}
                      className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                    >
                      <PauseIcon className="h-4 w-4 mr-2" />
                      Pause
                    </button>
                  )}
                </div>
              )}

              {/* Live Transcript */}
              {isRecording && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Live Transcript:</h4>
                  <p className="text-gray-800">{currentTranscript || 'Start speaking...'}</p>
                </div>
              )}

              {/* Final Transcript */}
              {currentAnswer?.transcript && !isRecording && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-green-700 mb-2">Your Response:</h4>
                  <p className="text-green-800">{currentAnswer.transcript}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Navigation & Progress */}
          <div className="space-y-6">
            {/* Progress */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress</h3>
              <div className="space-y-3">
                {test.questions.map((_, index) => {
                  const answer = session.answers.find(a => a.questionIndex === index)
                  const isCurrent = index === session.currentQuestion
                  const isAnswered = answer && answer.transcript
                  
                  return (
                    <div
                      key={index}
                      className={`flex items-center p-3 rounded-lg border ${
                        isCurrent 
                          ? 'border-blue-500 bg-blue-50' 
                          : isAnswered 
                            ? 'border-green-500 bg-green-50' 
                            : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                        isAnswered ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                      }`}>
                        {isAnswered ? <CheckCircleIcon className="h-4 w-4" /> : index + 1}
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        Question {index + 1}
                        {isAnswered && <span className="ml-2 text-green-600">✓</span>}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Navigation */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex justify-between">
                <button
                  onClick={previousQuestion}
                  disabled={session.currentQuestion === 0}
                  className="flex items-center px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <LeftArrowIcon className="h-4 w-4 mr-2" />
                  Previous
                </button>
                
                {isLastQuestion ? (
                  <button
                    onClick={submitTest}
                    disabled={session.answers.length === 0}
                    className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Test
                  </button>
                ) : (
                  <button
                    onClick={nextQuestion}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Next
                    <RightArrowIcon className="h-4 w-4 ml-2" />
                  </button>
                )}
              </div>
            </div>

            {/* Assessment Results */}
            {assessmentResult && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment Results</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-2">Overall Score</h4>
                    <p className="text-2xl font-bold text-blue-600">{assessmentResult.score?.overall || 'N/A'}/9.0</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                      <h5 className="font-semibold text-gray-700 mb-1">Fluency & Coherence</h5>
                      <p className="text-lg font-bold text-gray-600">{assessmentResult.score?.fluency || 'N/A'}/9.0</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                      <h5 className="font-semibold text-gray-700 mb-1">Lexical Resource</h5>
                      <p className="text-lg font-bold text-gray-600">{assessmentResult.score?.lexical || 'N/A'}/9.0</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                      <h5 className="font-semibold text-gray-700 mb-1">Grammar</h5>
                      <p className="text-lg font-bold text-gray-600">{assessmentResult.score?.grammar || 'N/A'}/9.0</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                      <h5 className="font-semibold text-gray-700 mb-1">Pronunciation</h5>
                      <p className="text-lg font-bold text-gray-600">{assessmentResult.score?.pronunciation || 'N/A'}/9.0</p>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-900 mb-2">Overall Feedback</h4>
                    <p className="text-green-800">{assessmentResult.feedback?.overall || 'No feedback available'}</p>
                  </div>

                  {assessmentResult.suggestions && assessmentResult.suggestions.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h4 className="font-semibold text-yellow-900 mb-2">Suggestions for Improvement</h4>
                      <ul className="list-disc list-inside text-yellow-800">
                        {assessmentResult.suggestions.map((suggestion: string, index: number) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onPause={() => setIsPlaying(false)}
      />
    </div>
  )
}
