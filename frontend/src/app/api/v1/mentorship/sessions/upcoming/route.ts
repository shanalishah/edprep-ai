// Vercel serverless function for upcoming sessions
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'

const users = [
  {
    id: 1,
    email: 'admin1@edprep.ai',
    username: 'admin1',
    full_name: 'Admin User 1',
    role: 'admin',
  },
  {
    id: 2,
    email: 'admin2@edprep.ai',
    username: 'admin2',
    full_name: 'Admin User 2',
    role: 'admin',
  },
  {
    id: 3,
    email: 'admin3@edprep.ai',
    username: 'admin3',
    full_name: 'Admin User 3',
    role: 'admin',
  }
]

// Sample sessions data
const sessions = [
  {
    id: 1,
    connection_id: 1,
    title: 'IELTS Writing Practice Session',
    description: 'Focus on Task 1 and Task 2 writing skills',
    session_type: 'writing',
    scheduled_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
    duration_minutes: 60,
    agenda: ['Warm-up discussion', 'Task 1 practice', 'Task 2 practice', 'Feedback and Q&A'],
    status: 'scheduled',
    mentor: users[0],
    mentee: users[1]
  },
  {
    id: 2,
    connection_id: 1,
    title: 'Speaking Practice Session',
    description: 'Practice speaking tasks and pronunciation',
    session_type: 'speaking',
    scheduled_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // Day after tomorrow
    duration_minutes: 45,
    agenda: ['Pronunciation warm-up', 'Part 1 practice', 'Part 2 practice', 'Part 3 discussion'],
    status: 'scheduled',
    mentor: users[0],
    mentee: users[1]
  }
]

function getCurrentUser(authHeader: string) {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null
  }
  
  const token = authHeader.split(' ')[1]
  try {
    const payload = jwt.verify(token, 'secret-key') as any
    return users.find(u => u.id === parseInt(payload.sub))
  } catch {
    return null
  }
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    const currentUser = getCurrentUser(authHeader || '')
    
    if (!currentUser) {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    // Filter sessions for current user (as mentor or mentee)
    const userSessions = sessions.filter(
      session => session.mentor.id === currentUser.id || session.mentee.id === currentUser.id
    )

    return NextResponse.json({
      success: true,
      sessions: userSessions,
      count: userSessions.length
    })

  } catch (error) {
    console.error('Get sessions error:', error)
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
