// API Configuration for production deployment
export const API_CONFIG = {
  // Railway backend URL
  BACKEND_URL: 'https://web-production-4d7f.up.railway.app',
  
  // Frontend URL (Vercel)
  FRONTEND_URL: 'https://ielts-master-platform-qrzlodk8y-shan-ali-shah-sayeds-projects.vercel.app',
  
  // API endpoints
  ENDPOINTS: {
    // Authentication (Railway backend)
    AUTH_LOGIN: '/api/v1/auth/login',
    AUTH_REGISTER: '/api/v1/auth/register',
    
    // User data (Railway backend)
    USER_PROFILE: '/api/v1/user/profile',
    USER_PROGRESS: '/api/v1/user/progress',
    
    // Essays and learning (Railway backend)
    ESSAYS_ASSESS: '/api/v1/essays/assess',
    LEARNING_SESSIONS: '/api/v1/learning/sessions',
    
    // Mentorship (Next.js API routes - frontend)
    MENTORSHIP_MENTORS: '/api/v1/mentorship/mentors',
    MENTORSHIP_CONNECTIONS: '/api/v1/mentorship/connections',
    MENTORSHIP_CONNECT: '/api/v1/mentorship/connect',
    MENTORSHIP_PROFILE: '/api/v1/mentorship/profile',
    MENTORSHIP_SESSIONS: '/api/v1/mentorship/sessions',
    MENTORSHIP_MESSAGES: '/api/v1/mentorship/connections',
    MENTORSHIP_WORKSPACE: '/api/v1/mentorship/connections'
  }
}

// Helper function to get full API URL
export const getApiUrl = (endpoint: string, useBackend: boolean = false): string => {
  const baseUrl = useBackend ? API_CONFIG.BACKEND_URL : API_CONFIG.FRONTEND_URL
  return `${baseUrl}${endpoint}`
}

// Helper function to get auth headers
export const getAuthHeaders = (token?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}
