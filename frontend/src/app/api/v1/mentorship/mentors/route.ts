// Vercel serverless function for mentorship mentors
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'

// Same data as in login route
const users = [
  {
    id: 1,
    email: 'admin1@edprep.ai',
    username: 'admin1',
    full_name: 'Admin User 1',
    role: 'admin',
    target_band_score: 8.5,
    current_level: 'advanced',
  },
  {
    id: 2,
    email: 'admin2@edprep.ai',
    username: 'admin2',
    full_name: 'Admin User 2',
    role: 'admin',
    target_band_score: 8.5,
    current_level: 'advanced',
  },
  {
    id: 3,
    email: 'admin3@edprep.ai',
    username: 'admin3',
    full_name: 'Admin User 3',
    role: 'admin',
    target_band_score: 8.5,
    current_level: 'advanced',
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

    const mentors = users.map(user => ({
      id: user.id,
      email: user.email,
      username: user.username,
      full_name: user.full_name,
      role: user.role,
      target_band_score: user.target_band_score,
      current_level: user.current_level,
      profile: {
        bio: `Experienced ${user.role} with expertise in IELTS preparation`,
        teaching_experience: "5+ years",
        specializations: ['Writing', 'Speaking', 'Reading', 'Listening'],
        average_rating: 4.8,
        total_mentees_helped: 50,
        is_available_for_mentorship: true
      }
    }))

    return NextResponse.json({
      success: true,
      mentors,
      count: mentors.length
    })

  } catch (error) {
    console.error('Get mentors error:', error)
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
