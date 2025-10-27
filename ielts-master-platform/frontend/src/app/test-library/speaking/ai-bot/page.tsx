'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  PauseIcon,
  SpeakerWaveIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../../../providers'

interface BotSession {
  session_id: string
  welcome_message: string
  test_info: {
    title: string
    total_parts: number
    estimated_duration: string
    current_part: number
  }
  bot_personality: {
    name: string
    role: string
    personality: string
    speaking_style: string
  }
}

interface BotResponse {
  bot_response: {
    text: string
    audio_url?: string
    question_type: string
    part: number
    question_number: number
  }
  session_state: {
    current_part: number
    current_question: number
    progress_percentage: number
    time_elapsed: string
  }
  response_analysis: {
    fluency_score: number
    coherence_score: number
    lexical_resource_score: number
    grammar_score: number
    pronunciation_score: number
    overall_score: number
    strengths: string[]
    areas_for_improvement: string[]
  }
}

interface TestResults {
  session_summary: {
    test_id: string
    duration: string
    total_responses: number
    parts_completed: number
  }
  assessment: {
    overall_score: number
    fluency_score: number
    coherence_score: number
    lexical_resource_score: number
    grammar_score: number
    pronunciation_score: number
    band_level: string
  }
  closing_message: string
  detailed_feedback: Array<{
    part: string
    score: number
    strengths: string
    improvements: string
  }>
  improvement_suggestions: string[]
}

export default function AISpeakingBotPage() {
  const router = useRouter()
  const { user } = useAuth()

  const [session, setSession] = useState<BotSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [botMessages, setBotMessages] = useState<Array<{role: 'bot' | 'user', content: string, timestamp: Date}>>([])
  const [sessionState, setSessionState] = useState<any>(null)
  const [testResults, setTestResults] = useState<TestResults | null>(null)
  const [error, setError] = useState<string | null>(null)

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

  const startBotTest = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ai-speaking-bot/start-bot-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token || 'guest-token'}`
        },
        body: JSON.stringify({
          test_id: 'ai_speaking_bot_test',
          user_profile: {
            name: user?.name || 'Guest User',
            level: 'intermediate'
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to start AI speaking test')
      }

      const data = await response.json()
      setSession(data.session_data)
      
      // Add welcome message to chat
      setBotMessages([{
        role: 'bot',
        content: data.session_data.welcome_message,
        timestamp: new Date()
      }])

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start test')
    } finally {
      setIsLoading(false)
    }
  }

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
        // Process the audio and send to bot
        processUserResponse(currentTranscript)
        
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

  const processUserResponse = async (userResponse: string) => {
    if (!session || !userResponse.trim()) return

    try {
      // Add user message to chat
      setBotMessages(prev => [...prev, {
        role: 'user',
        content: userResponse,
        timestamp: new Date()
      }])

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ai-speaking-bot/process-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token || 'guest-token'}`
        },
        body: JSON.stringify({
          session_id: session.session_id,
          user_response: userResponse
        })
      })

      if (!response.ok) {
        throw new Error('Failed to process response')
      }

      const data = await response.json()
      const botResponse: BotResponse = data.response_data

      // Add bot response to chat
      setBotMessages(prev => [...prev, {
        role: 'bot',
        content: botResponse.bot_response.text,
        timestamp: new Date()
      }])

      // Update session state
      setSessionState(botResponse.session_state)

      // Check if test is complete
      if (botResponse.session_state.progress_percentage >= 100) {
        completeTest()
      }

    } catch (err) {
      console.error('Error processing response:', err)
      setError('Failed to process response')
    }
  }

  const completeTest = async () => {
    if (!session) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ai-speaking-bot/complete-bot-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token || 'guest-token'}`
        },
        body: JSON.stringify({
          session_id: session.session_id
        })
      })

      if (!response.ok) {
        throw new Error('Failed to complete test')
      }

      const data = await response.json()
      setTestResults(data.results)

      // Add closing message to chat
      setBotMessages(prev => [...prev, {
        role: 'bot',
        content: data.results.closing_message,
        timestamp: new Date()
      }])

    } catch (err) {
      console.error('Error completing test:', err)
      setError('Failed to complete test')
    }
  }

  const playBotAudio = (text: string) => {
    // This would use text-to-speech to play the bot's response
    // For now, we'll just show the text
    console.log('Playing bot audio:', text)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Starting AI Speaking Test...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Error</h1>
          <p className="text-gray-600 mb-4">{error}</p>
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
                <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
                Back to Speaking Tests
              </button>
              <div className="h-6 w-px bg-gray-300" />
              <h1 className="text-lg font-semibold text-gray-900">AI Speaking Test Bot</h1>
            </div>
            
            {sessionState && (
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm text-gray-600">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  {sessionState.time_elapsed}
                </div>
                <div className="text-sm text-gray-600">
                  Part {sessionState.current_part} - Question {sessionState.current_question + 1}
                </div>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${sessionState.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!session ? (
          /* Start Test Screen */
          <div className="text-center">
            <div className="bg-white rounded-lg shadow-sm p-8 max-w-2xl mx-auto">
              <div className="mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Speaking Test Bot</h2>
                <p className="text-gray-600">
                  Experience a realistic IELTS speaking test with our AI examiner bot. 
                  Have a natural conversation and receive comprehensive feedback.
                </p>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  <span>Voice-to-voice conversation</span>
                </div>
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  <span>Real-time assessment</span>
                </div>
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  <span>Comprehensive feedback</span>
                </div>
              </div>

              <button
                onClick={startBotTest}
                className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
                Start AI Speaking Test
              </button>
            </div>
          </div>
        ) : (
          /* Test Interface */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chat Interface */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Conversation with {session.bot_personality.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {session.bot_personality.role} • {session.bot_personality.personality}
                </p>
              </div>

              {/* Chat Messages */}
              <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-4 space-y-4">
                {botMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Recording Controls */}
              <div className="flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <MicrophoneIcon className="h-5 w-5 mr-2" />
                    Start Speaking
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

              {/* Live Transcript */}
              {isRecording && (
                <div className="mt-4 bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Live Transcript:</h4>
                  <p className="text-gray-800">{currentTranscript || 'Start speaking...'}</p>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Test Progress */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Progress</h3>
                {sessionState ? (
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Part {sessionState.current_part} of 3</span>
                      <span>{sessionState.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${sessionState.progress_percentage}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-600">
                      Time: {sessionState.time_elapsed}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Test not started yet</p>
                )}
              </div>

              {/* Test Results */}
              {testResults && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Results</h3>
                  <div className="space-y-4">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-900 mb-2">Overall Score</h4>
                      <p className="text-2xl font-bold text-blue-600">{testResults.assessment.overall_score}/9.0</p>
                      <p className="text-sm text-blue-700">{testResults.assessment.band_level}</p>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                        <h5 className="font-semibold text-gray-700 mb-1">Fluency</h5>
                        <p className="text-lg font-bold text-gray-600">{testResults.assessment.fluency_score}/9.0</p>
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                        <h5 className="font-semibold text-gray-700 mb-1">Coherence</h5>
                        <p className="text-lg font-bold text-gray-600">{testResults.assessment.coherence_score}/9.0</p>
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                        <h5 className="font-semibold text-gray-700 mb-1">Vocabulary</h5>
                        <p className="text-lg font-bold text-gray-600">{testResults.assessment.lexical_resource_score}/9.0</p>
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                        <h5 className="font-semibold text-gray-700 mb-1">Grammar</h5>
                        <p className="text-lg font-bold text-gray-600">{testResults.assessment.grammar_score}/9.0</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Improvement Suggestions */}
              {testResults && testResults.improvement_suggestions.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Suggestions</h3>
                  <ul className="space-y-2">
                    {testResults.improvement_suggestions.map((suggestion, index) => (
                      <li key={index} className="flex items-start space-x-2 text-sm text-gray-700">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
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
