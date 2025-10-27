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
    username: 'mentor1',
    full_name: 'Mentor One',
    email: 'mentor1@edprep.ai',
    role: 'mentor',
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
    username: 'mentor2',
    full_name: 'Mentor Two',
    email: 'mentor2@edprep.ai',
    role: 'mentor',
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
    username: 'mentor3',
    full_name: 'Mentor Three',
    email: 'mentor3@edprep.ai',
    role: 'mentor',
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

// Shared connections array - use getter/setter functions
let _connections: any[] = [
  // Demo connections for testing
  {
    id: 1,
    mentor_id: 2,
    mentee_id: 1,
    status: 'pending',
    connection_message: "Let's work together on IELTS preparation!",
    goals: ['Improve IELTS score', 'Get personalized feedback'],
    target_band_score: 7.5,
    focus_areas: ['Writing', 'Speaking'],
    created_at: new Date().toISOString(),
    mentor: mentors[1], // admin2
    mentee: users[0]    // admin1
  },
  {
    id: 2,
    mentor_id: 3,
    mentee_id: 1,
    status: 'pending',
    connection_message: "I'd love to help you improve your IELTS skills!",
    goals: ['Achieve band 8', 'Focus on speaking'],
    target_band_score: 8.0,
    focus_areas: ['Speaking', 'Listening'],
    created_at: new Date().toISOString(),
    mentor: mentors[2], // admin3
    mentee: users[0]    // admin1
  }
]
let _connectionIdCounter = 3

export function getConnections() {
  return _connections
}

export function addConnection(connection: any) {
  connection.id = _connectionIdCounter++
  _connections.push(connection)
  return connection
}

export function updateConnection(connectionId: number, updates: any) {
  const index = _connections.findIndex(c => c.id === connectionId)
  if (index !== -1) {
    _connections[index] = { ..._connections[index], ...updates }
    return _connections[index]
  }
  return null
}

export function removeConnection(connectionId: number) {
  const index = _connections.findIndex(c => c.id === connectionId)
  if (index !== -1) {
    return _connections.splice(index, 1)[0]
  }
  return null
}

export function getConnectionIdCounter() {
  return _connectionIdCounter
}

// Shared messages array
let _messages: any[] = []
let _messageIdCounter = 1

export function getMessages() {
  return _messages
}

export function addMessage(message: any) {
  message.id = _messageIdCounter++
  _messages.push(message)
  return message
}

// Shared sessions array
let _sessions: any[] = []
let _sessionIdCounter = 1

export function getSessions() {
  return _sessions
}

export function addSession(session: any) {
  session.id = _sessionIdCounter++
  _sessions.push(session)
  return session
}
