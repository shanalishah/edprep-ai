'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../providers';
import { useRouter } from 'next/navigation';
import { useUserData } from '../../hooks/useUserData';
import { motion, AnimatePresence } from 'framer-motion';
import { Tab } from '@headlessui/react';
import { 
  BookOpenIcon, 
  ChartBarIcon, 
  SparklesIcon, 
  UserGroupIcon,
  ClockIcon,
  TrophyIcon,
  FireIcon,
  StarIcon,
  ArrowTrendingUpIcon,
  UserIcon,
  AcademicCapIcon,
  LightBulbIcon,
  DocumentTextIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ErrorAnalysis {
  l1_influenced: string[];
  interlanguage: string[];
  discourse_management: string[];
}

interface FeedbackDetail {
  detailed_feedback: string;
  suggestions: string[];
  error_analysis: ErrorAnalysis;
}

interface ScoringResult {
  task_achievement: number;
  coherence_cohesion: number;
  lexical_resource: number;
  grammatical_range: number;
  overall_band_score: number;
  feedback: FeedbackDetail;
  confidence: number;
  scoring_method: string;
  timestamp: string;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function DashboardPage() {
  const { isAuthenticated, user, logout, loading: authLoading } = useAuth();
  const { userProfile, loading: userDataLoading, error: userDataError, refetch } = useUserData();
  const router = useRouter();
  const [essay, setEssay] = useState('');
  const [prompt, setPrompt] = useState('Some people believe that technology has made our lives more complicated, while others think it has made life easier. Discuss both views and give your opinion.');
  const [result, setResult] = useState<ScoringResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleSubmit = async () => {
    if (!essay.trim()) {
      setError('Please write an essay before submitting.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      
      // Transform the response to match our expected structure
      const data: ScoringResult = {
        task_achievement: responseData.scores?.task_achievement || 0,
        coherence_cohesion: responseData.scores?.coherence_cohesion || 0,
        lexical_resource: responseData.scores?.lexical_resource || 0,
        grammatical_range: responseData.scores?.grammatical_range || 0,
        overall_band_score: responseData.scores?.overall_band_score || 0,
        feedback: {
          detailed_feedback: responseData.feedback?.detailed_feedback || 'No feedback available',
          suggestions: responseData.feedback?.suggestions || [],
          error_analysis: {
            l1_influenced: responseData.feedback?.error_analysis?.l1_influenced || [],
            interlanguage: responseData.feedback?.error_analysis?.interlanguage || [],
            discourse_management: responseData.feedback?.error_analysis?.discourse_management || []
          }
        },
        confidence: responseData.assessment_metadata?.confidence || 0,
        scoring_method: responseData.assessment_metadata?.assessment_method || 'unknown',
        timestamp: new Date().toISOString()
      };
      
      setResult(data);
      
      // Refresh user data after successful assessment (only for real users, not guests)
      if (!isGuest) {
        refetch();
      }
    } catch (err: any) {
      setError(err.message);
      if (err.message.includes('Authentication token not found') || err.message.includes('Invalid authentication credentials')) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  const isGuest = user?.isGuest;

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <header className="glass-effect border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-4"
            >
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <span className="text-2xl">🎓</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">IELTS Master Platform</h1>
                <p className="text-white/80 text-sm">
                  {isGuest ? 'Guest Mode' : `Welcome back, ${user?.email}`}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-4"
            >
              {!isGuest && (
                <div className="flex items-center space-x-3 text-white/90">
                  <div className="flex items-center space-x-1">
                    <FireIcon className="h-5 w-5 text-orange-400" />
                    <span className="text-sm font-medium">{userProfile?.stats?.streak_days || 0} day streak</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <TrophyIcon className="h-5 w-5 text-yellow-400" />
                    <span className="text-sm font-medium">{userProfile?.stats?.total_points?.toLocaleString() || 0} points</span>
                  </div>
                </div>
              )}
              
              <button
                onClick={logout}
                className="btn-secondary text-sm"
              >
                <UserIcon className="h-4 w-4 mr-2" />
                {isGuest ? 'Exit Guest Mode' : 'Logout'}
              </button>
            </motion.div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-1"
          >
            <div className="glass-effect rounded-2xl p-6">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab(0)}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                    activeTab === 0
                      ? 'bg-primary-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-white/50 hover:text-gray-900'
                  }`}
                >
                  <SparklesIcon className="h-5 w-5 mr-3" />
                  Writing Assessment
                </button>
                <button
                  onClick={() => setActiveTab(1)}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                    activeTab === 1
                      ? 'bg-primary-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-white/50 hover:text-gray-900'
                  }`}
                >
                  <BookOpenIcon className="h-5 w-5 mr-3" />
                  Learning Center
                </button>
                <button
                  onClick={() => setActiveTab(2)}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                    activeTab === 2
                      ? 'bg-primary-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-white/50 hover:text-gray-900'
                  }`}
                >
                  <ChartBarIcon className="h-5 w-5 mr-3" />
                  Analytics
                </button>
                <button
                  className="w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl text-gray-700 hover:bg-white/50 hover:text-gray-900 transition-all duration-200"
                >
                  <UserGroupIcon className="h-5 w-5 mr-3" />
                  Social Learning
                </button>
              </nav>

              {/* Quick Stats */}
              <div className="mt-8 pt-6 border-t border-white/20">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Essays Written</span>
                    <span className="text-sm font-semibold text-gray-900">{userProfile?.progress?.essays_written || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Average Score</span>
                    <span className="text-sm font-semibold text-gray-900">{userProfile?.progress?.average_score?.toFixed(1) || '0.0'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Best Score</span>
                    <span className="text-sm font-semibold text-gray-900">{userProfile?.progress?.best_score?.toFixed(1) || '0.0'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Level</span>
                    <span className="text-sm font-semibold text-gray-900 capitalize">{userProfile?.stats?.current_level || 'Beginner'}</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Main Content Area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-3"
          >
            <AnimatePresence mode="wait">
              {activeTab === 0 && (
                <motion.div
                  key="assessment"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  {/* Assessment Form */}
                  <div className="glass-effect rounded-2xl p-8">
                    <div className="flex items-center mb-6">
                      <div className="w-12 h-12 bg-primary-500 rounded-2xl flex items-center justify-center mr-4">
                        <PencilIcon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">Writing Assessment</h2>
                        <p className="text-gray-600">Get instant AI-powered feedback on your IELTS essays</p>
                      </div>
                    </div>
                    
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Writing Prompt:
                        </label>
                        <textarea
                          value={prompt}
                          onChange={(e) => setPrompt(e.target.value)}
                          className="input w-full h-24 resize-none"
                          placeholder="Enter your IELTS writing prompt..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Your Essay:
                        </label>
                        <textarea
                          value={essay}
                          onChange={(e) => setEssay(e.target.value)}
                          className="input w-full h-64 resize-none"
                          placeholder="Write your essay here..."
                        />
                        <div className="mt-2 text-sm text-gray-500">
                          Word count: {essay.split(/\s+/).filter(word => word.length > 0).length}
                        </div>
                      </div>

                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleSubmit}
                        disabled={loading}
                        className="btn-primary w-full btn-lg relative overflow-hidden"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center">
                            <div className="loading-spinner mr-2"></div>
                            Assessing Essay...
                          </div>
                        ) : (
                          <>
                            <SparklesIcon className="h-5 w-5 mr-2" />
                            Assess Essay
                          </>
                        )}
                      </motion.button>

                      {error && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded-xl"
                        >
                          <strong>Error:</strong> {error}
                        </motion.div>
                      )}
                    </div>
                  </div>

                  {/* Results */}
                  {result && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="glass-effect rounded-2xl p-8"
                    >
                      <div className="flex items-center mb-6">
                        <div className="w-12 h-12 bg-success-500 rounded-2xl flex items-center justify-center mr-4">
                          <TrophyIcon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h2 className="text-2xl font-bold text-gray-900">Assessment Results</h2>
                          <p className="text-gray-600">Detailed analysis of your essay</p>
                        </div>
                      </div>
                      
                      {/* Score Cards */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
                        {Object.entries({
                          'Task Achievement': result.task_achievement,
                          'Coherence & Cohesion': result.coherence_cohesion,
                          'Lexical Resource': result.lexical_resource,
                          'Grammar Range': result.grammatical_range,
                          'Overall Band Score': result.overall_band_score,
                        }).map(([criterion, score]) => (
                          <motion.div
                            key={criterion}
                            whileHover={{ scale: 1.05 }}
                            className="education-card p-4 text-center"
                          >
                            <div className="text-xs text-gray-600 mb-1">{criterion}</div>
                            <div className="text-2xl font-bold text-primary-600">{score?.toFixed(1) || 'N/A'}</div>
                          </motion.div>
                        ))}
                      </div>

                      {/* Feedback */}
                      <div className="space-y-6">
                        <div className="bg-primary-50 p-6 rounded-xl">
                          <h3 className="font-semibold text-primary-800 mb-3 flex items-center">
                            <LightBulbIcon className="h-5 w-5 mr-2" />
                            Detailed Feedback
                          </h3>
                          <div className="prose prose-sm max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {result.feedback.detailed_feedback || 'No feedback available'}
                            </ReactMarkdown>
                          </div>
                        </div>

                        {result.feedback.suggestions && result.feedback.suggestions.length > 0 && (
                          <div className="bg-success-50 p-6 rounded-xl">
                            <h3 className="font-semibold text-success-800 mb-3 flex items-center">
                              <AcademicCapIcon className="h-5 w-5 mr-2" />
                              Suggestions for Improvement
                            </h3>
                            <ul className="space-y-2">
                              {result.feedback.suggestions.map((suggestion, i) => (
                                <li key={i} className="flex items-start">
                                  <span className="text-success-600 mr-2">•</span>
                                  <span className="text-gray-700">{suggestion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Error Analysis */}
                        {(result.feedback.error_analysis && 
                          ((result.feedback.error_analysis.l1_influenced && result.feedback.error_analysis.l1_influenced.length > 0) ||
                           (result.feedback.error_analysis.interlanguage && result.feedback.error_analysis.interlanguage.length > 0) ||
                           (result.feedback.error_analysis.discourse_management && result.feedback.error_analysis.discourse_management.length > 0))) && (
                          <div className="bg-warning-50 p-6 rounded-xl">
                            <h3 className="font-semibold text-warning-800 mb-3 flex items-center">
                              <DocumentTextIcon className="h-5 w-5 mr-2" />
                              Error Analysis
                            </h3>
                            <div className="space-y-4">
                              {result.feedback.error_analysis.l1_influenced && result.feedback.error_analysis.l1_influenced.length > 0 && (
                                <div>
                                  <h4 className="font-medium text-warning-700 mb-2">L1-Influenced Mistakes:</h4>
                                  <ul className="space-y-1">
                                    {result.feedback.error_analysis.l1_influenced.map((error, i) => (
                                      <li key={i} className="text-sm text-gray-700 flex items-start">
                                        <span className="text-warning-600 mr-2">•</span>
                                        {error}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {result.feedback.error_analysis.interlanguage && result.feedback.error_analysis.interlanguage.length > 0 && (
                                <div>
                                  <h4 className="font-medium text-warning-700 mb-2">Interlanguage Mistakes:</h4>
                                  <ul className="space-y-1">
                                    {result.feedback.error_analysis.interlanguage.map((error, i) => (
                                      <li key={i} className="text-sm text-gray-700 flex items-start">
                                        <span className="text-warning-600 mr-2">•</span>
                                        {error}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {result.feedback.error_analysis.discourse_management && result.feedback.error_analysis.discourse_management.length > 0 && (
                                <div>
                                  <h4 className="font-medium text-warning-700 mb-2">Discourse Management:</h4>
                                  <ul className="space-y-1">
                                    {result.feedback.error_analysis.discourse_management.map((error, i) => (
                                      <li key={i} className="text-sm text-gray-700 flex items-start">
                                        <span className="text-warning-600 mr-2">•</span>
                                        {error}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {activeTab === 1 && (
                <motion.div
                  key="learning"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="glass-effect rounded-2xl p-8"
                >
                  <div className="text-center">
                    <div className="w-16 h-16 bg-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <BookOpenIcon className="h-8 w-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Learning Center</h2>
                    <p className="text-gray-600 mb-6">Coming Soon! Personalized learning modules and AI teaching roles.</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="education-card p-6 text-center">
                        <div className="text-3xl mb-2">🤖</div>
                        <h3 className="font-semibold text-gray-900 mb-2">AI Teaching Roles</h3>
                        <p className="text-sm text-gray-600">Questionnaire, Explainer, and Challenger bots</p>
                      </div>
                      <div className="education-card p-6 text-center">
                        <div className="text-3xl mb-2">🎮</div>
                        <h3 className="font-semibold text-gray-900 mb-2">Gamification</h3>
                        <p className="text-sm text-gray-600">Points, achievements, and leaderboards</p>
                      </div>
                      <div className="education-card p-6 text-center">
                        <div className="text-3xl mb-2">👥</div>
                        <h3 className="font-semibold text-gray-900 mb-2">Social Learning</h3>
                        <p className="text-sm text-gray-600">Mentor-mentee and peer learning</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 2 && (
                <motion.div
                  key="analytics"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="glass-effect rounded-2xl p-8"
                >
                  <div className="text-center">
                    <div className="w-16 h-16 bg-success-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <ChartBarIcon className="h-8 w-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Analytics Dashboard</h2>
                    <p className="text-gray-600 mb-6">Track your progress and identify improvement areas.</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="education-card p-6">
                        <h3 className="font-semibold text-gray-900 mb-4">Progress Tracking</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Writing Score Trend</span>
                            <span className="text-success-600 font-semibold">↗ +0.5</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Grammar Improvement</span>
                            <span className="text-success-600 font-semibold">↗ +0.3</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Vocabulary Range</span>
                            <span className="text-warning-600 font-semibold">→ 0.0</span>
                          </div>
                        </div>
                      </div>
                      <div className="education-card p-6">
                        <h3 className="font-semibold text-gray-900 mb-4">Performance Insights</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Strongest Area</span>
                            <span className="text-success-600 font-semibold">Task Achievement</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Needs Focus</span>
                            <span className="text-warning-600 font-semibold">Lexical Resource</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Next Goal</span>
                            <span className="text-primary-600 font-semibold">Band 7.0</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  );
}