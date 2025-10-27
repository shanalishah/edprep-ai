// Shared data store for all API routes
export const users = [
  {
    id: 1,
    email: 'admin1@edprep.ai',
    username: 'admin1',
    full_name: 'Admin User 1',
    password: '$2b$10$LgA4KTs01JITFrFPd/bJZe2agXwLuaiIt1MaHsORq.Ynmbfw/eMV6', // 'test'
    role: 'admin',
    is_active: true,
    is_verified: true,
    is_premium: true,
    target_band_score: 8.5,
    current_level: 'advanced',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_login: null,
    total_points: 0,
    level: 1,
    streak_days: 0
  },
  {
    id: 2,
    email: 'admin2@edprep.ai',
    username: 'admin2',
    full_name: 'Admin User 2',
    password: '$2b$10$LgA4KTs01JITFrFPd/bJZe2agXwLuaiIt1MaHsORq.Ynmbfw/eMV6', // 'test'
    role: 'admin',
    is_active: true,
    is_verified: true,
    is_premium: true,
    target_band_score: 8.0,
    current_level: 'advanced',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_login: null,
    total_points: 0,
    level: 1,
    streak_days: 0
  },
  {
    id: 3,
    email: 'admin3@edprep.ai',
    username: 'admin3',
    full_name: 'Admin User 3',
    password: '$2b$10$LgA4KTs01JITFrFPd/bJZe2agXwLuaiIt1MaHsORq.Ynmbfw/eMV6', // 'test'
    role: 'admin',
    is_active: true,
    is_verified: true,
    is_premium: true,
    target_band_score: 7.5,
    current_level: 'intermediate',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_login: null,
    total_points: 0,
    level: 1,
    streak_days: 0
  }
]

export const mentors = [
  {
    id: 1,
    username: 'admin1',
    full_name: 'Admin User 1',
    email: 'admin1@edprep.ai',
    role: 'admin',
    target_band_score: 8.5,
    current_level: 'advanced',
    profile: {
      bio: 'Experienced IELTS instructor with 10+ years of teaching experience. Specialized in Writing and Speaking modules.',
      teaching_experience: '10+ years',
      specializations: ['Writing', 'Speaking', 'Academic English'],
      average_rating: 4.8,
      total_mentees_helped: 150,
      is_available_for_mentorship: true,
      timezone: 'GMT+5',
      available_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      available_hours: ['09:00-17:00'],
      max_mentees: 5
    }
  },
  {
    id: 2,
    username: 'admin2',
    full_name: 'Admin User 2',
    email: 'admin2@edprep.ai',
    role: 'admin',
    target_band_score: 8.0,
    current_level: 'advanced',
    profile: {
      bio: 'IELTS expert focusing on Reading and Listening strategies. Helps students achieve their target band scores.',
      teaching_experience: '8+ years',
      specializations: ['Reading', 'Listening', 'Test Strategies'],
      average_rating: 4.7,
      total_mentees_helped: 120,
      is_available_for_mentorship: true,
      timezone: 'GMT+0',
      available_days: ['Monday', 'Wednesday', 'Friday', 'Saturday'],
      available_hours: ['10:00-18:00'],
      max_mentees: 4
    }
  },
  {
    id: 3,
    username: 'admin3',
    full_name: 'Admin User 3',
    email: 'admin3@edprep.ai',
    role: 'admin',
    target_band_score: 7.5,
    current_level: 'intermediate',
    profile: {
      bio: 'Comprehensive IELTS preparation specialist. Covers all four modules with personalized study plans.',
      teaching_experience: '6+ years',
      specializations: ['All Modules', 'Study Planning', 'Time Management'],
      average_rating: 4.6,
      total_mentees_helped: 80,
      is_available_for_mentorship: true,
      timezone: 'GMT-5',
      available_days: ['Tuesday', 'Thursday', 'Saturday', 'Sunday'],
      available_hours: ['14:00-22:00'],
      max_mentees: 3
    }
  }
]

// Shared connections array
export let connections: any[] = []

// Shared messages array
export let messages: any[] = []

// Shared sessions array
export let sessions: any[] = []

// Counter for generating IDs
export let connectionIdCounter = 1
export let messageIdCounter = 1
export let sessionIdCounter = 1
