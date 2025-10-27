// Vercel serverless function for mentorship connections
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'

// Same data as in other routes
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

const connections = [
  {
    id: 1,
    mentor_id: 1,
    mentee_id: 2,
    status: 'active',
    connection_message: "Let's work together on IELTS preparation!",
    goals: ['Improve IELTS score', 'Get personalized feedback'],
    target_band_score: 7.5,
    focus_areas: ['Writing', 'Speaking'],
    created_at: new Date().toISOString(),
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

    // Filter connections for current user
    const userConnections = connections.filter(
      conn => conn.mentor_id === currentUser.id || conn.mentee_id === currentUser.id
    )

    return NextResponse.json({
      success: true,
      connections: userConnections,
      count: userConnections.length
    })

  } catch (error) {
    console.error('Get connections error:', error)
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
