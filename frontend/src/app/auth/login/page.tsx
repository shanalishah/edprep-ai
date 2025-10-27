'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../providers'
import { 
  EyeIcon, 
  EyeSlashIcon, 
  XCircleIcon,
  UserIcon,
  ArrowRightIcon,
  SparklesIcon,
  BookOpenIcon,
  ChartBarIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { supabase } from '../../../lib/supabaseClient'
import { getApiUrl, API_CONFIG } from '../../../lib/api-config'

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional()
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  const onSubmit = async (data: LoginFormData) => {
    console.log('Form data:', data) // Debug log
    setIsLoading(true)
    try {
      const provider = process.env.NEXT_PUBLIC_AUTH_PROVIDER || 'backend'
      console.log('🔧 Provider:', provider) // Debug log
      if (provider === 'supabase' && supabase) {
        const { data: auth, error } = await supabase.auth.signInWithPassword({
          email: data.email,
          password: data.password
        })
        if (error) throw new Error(error.message)
        const user = auth.user
        // fetch profile for display info
        const { data: profile } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single()
        login(auth.session?.access_token || 'supabase', {
          id: user.id,
          email: user.email,
          username: profile?.username || user.email?.split('@')[0],
          full_name: profile?.full_name || user.email,
          role: profile?.role || 'student'
        })
        toast.success('Welcome back!')
        router.push('/dashboard')
      } else {
        // Use Railway backend for authentication
        console.log('🚀 Using Railway backend for authentication') // Debug log
        const formData = new URLSearchParams()
        formData.append('username', data.email)
        formData.append('password', data.password)
        const apiUrl = getApiUrl(API_CONFIG.ENDPOINTS.AUTH_LOGIN, true)
        console.log('🚀 Sending login request to Railway backend:', { email: data.email, password: '***', apiUrl }) // Debug log
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString(),
        })
        if (!response.ok) {
          const errorData = await response.json()
          console.error('Login error response:', errorData) // Debug log
          throw new Error(errorData.detail || 'Login failed')
        }
        const result = await response.json()
        login(result.access_token, result.user)
        toast.success('Welcome back!')
        router.push('/dashboard')
      }
      
    } catch (error: any) {
      console.error('Login error:', error) // Debug log
      toast.error(error.message || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGuestLogin = () => {
    console.log('Guest login clicked')
    const guestToken = 'guest_' + Date.now()
    console.log('Guest token:', guestToken)
    try {
      login(guestToken, { 
        id: 999, 
        email: 'guest@ieltsmaster.com', 
        username: 'guest',
        full_name: 'Guest User',
        isGuest: true 
      })
      toast.success('Welcome! You are now logged in as a guest.')
      console.log('Redirecting to dashboard...')
      router.push('/dashboard')
    } catch (error) {
      console.error('Guest login error:', error)
      toast.error('Failed to login as guest')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b sticky top-0 z-50">
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
              <Link href="/writing-coach" className="text-gray-600 hover:text-gray-900 transition-colors">Writing Coach</Link>
              <Link href="/tips" className="text-gray-600 hover:text-gray-900 transition-colors">Tips</Link>
              <Link href="/analytics" className="text-gray-600 hover:text-gray-900 transition-colors">Analytics</Link>
            </nav>
            <div className="flex items-center space-x-4">
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

      <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-6 shadow-xl"
            >
              <span className="text-4xl">🎓</span>
            </motion.div>
            
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Welcome Back
            </h1>
            <p className="text-lg text-gray-600">
              Sign in to continue your IELTS preparation journey
            </p>
          </motion.div>


          {/* Login Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20"
          >
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Sign In</h2>
              <p className="text-gray-600">Enter your credentials to access your account</p>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Email */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700">
                  Email Address
                </label>
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  className={`w-full px-4 py-3 text-lg border-2 rounded-xl transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-200/50 ${
                    errors.email 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-200/50' 
                      : 'border-gray-200 focus:border-blue-500'
                  } bg-white/90 backdrop-blur-sm`}
                  placeholder="Enter your email address"
                  autoComplete="email"
                />
                {errors.email && (
                  <p className="mt-2 text-sm text-red-600 flex items-center font-medium">
                    <XCircleIcon className="h-4 w-4 mr-2" />
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Password */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                  Password
                </label>
                <div className="relative">
                  <input
                    {...register('password')}
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    className={`w-full px-4 py-3 text-lg border-2 rounded-xl transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-200/50 pr-12 ${
                      errors.password 
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-200/50' 
                        : 'border-gray-200 focus:border-blue-500'
                    } bg-white/90 backdrop-blur-sm`}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-gray-50 rounded-r-xl transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-500" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-500" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-2 text-sm text-red-600 flex items-center font-medium">
                    <XCircleIcon className="h-4 w-4 mr-2" />
                    {errors.password.message}
                  </p>
                )}
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between pt-2">
                <label className="flex items-center cursor-pointer">
                  <input
                    {...register('rememberMe')}
                    type="checkbox"
                    className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded-lg transition-colors"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-700">Remember me</span>
                </label>
                
                <Link 
                  href="/auth/forgot-password" 
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-200/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    <span className="text-lg">Signing In...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <span className="text-lg">Sign In</span>
                    <ArrowRightIcon className="ml-2 h-5 w-5" />
                  </div>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500 font-medium">Or continue with</span>
                </div>
              </div>

              {/* Guest Login */}
              <div className="mt-6">
                <button
                  type="button"
                  onClick={handleGuestLogin}
                  className="w-full inline-flex justify-center items-center py-3 px-6 border-2 border-blue-200 rounded-xl shadow-sm bg-blue-50 text-lg font-semibold text-blue-700 hover:bg-blue-100 hover:border-blue-300 transition-all duration-200 transform hover:scale-[1.01]"
                >
                  <UserIcon className="h-6 w-6 mr-3" />
                  Try Demo (Guest Access)
                </button>
              </div>

              {/* Social Login */}
              <div className="mt-4 grid grid-cols-2 gap-4">
                <button
                  type="button"
                  className="w-full inline-flex justify-center items-center py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 transform hover:scale-[1.01]"
                >
                  <svg className="h-5 w-5" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span className="ml-2">Google</span>
                </button>

                <button
                  type="button"
                  className="w-full inline-flex justify-center items-center py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 transform hover:scale-[1.01]"
                >
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  <span className="ml-2">Facebook</span>
                </button>
              </div>
            </div>

            {/* Register Link */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link href="/auth/register" className="text-blue-600 hover:text-blue-700 font-semibold transition-colors">
                  Create one here
                </Link>
              </p>
            </div>
          </motion.div>

          {/* Features Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-3 gap-4 text-center"
          >
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <BookOpenIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-semibold text-gray-700">100+ Tests</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <ChartBarIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <p className="text-sm font-semibold text-gray-700">AI Analytics</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <AcademicCapIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <p className="text-sm font-semibold text-gray-700">Expert Tips</p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}