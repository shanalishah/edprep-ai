// Vercel serverless function for authentication
import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'

// In-memory database (in production, use a real database)
const users = [
  {
    id: 1,
    email: 'admin1@edprep.ai',
    username: 'admin1',
    full_name: 'Admin User 1',
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // 'test'
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
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // 'test'
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
    id: 3,
    email: 'admin3@edprep.ai',
    username: 'admin3',
    full_name: 'Admin User 3',
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // 'test'
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

const messages = [
  {
    id: 1,
    connection_id: 1,
    sender_id: 1,
    message_type: 'text',
    content: 'Welcome! I\'m excited to help you with your IELTS preparation.',
    file_url: null,
    file_name: null,
    file_size: null,
    is_read: false,
    read_at: null,
    is_edited: false,
    edited_at: null,
    created_at: new Date().toISOString(),
    sender: users[0]
  },
  {
    id: 2,
    connection_id: 1,
    sender_id: 2,
    message_type: 'text',
    content: 'Thank you! I\'m looking forward to improving my writing skills.',
    file_url: null,
    file_name: null,
    file_size: null,
    is_read: false,
    read_at: null,
    is_edited: false,
    edited_at: null,
    created_at: new Date().toISOString(),
    sender: users[1]
  }
]

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const username = formData.get('username') as string
    const password = formData.get('password') as string

    if (!username || !password) {
      return NextResponse.json(
        { detail: 'Username and password required' },
        { status: 400 }
      )
    }

    // Find user
    const user = users.find(u => u.email === username)
    if (!user) {
      return NextResponse.json(
        { detail: 'Invalid email/username or password' },
        { status: 401 }
      )
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password)
    if (!isValidPassword) {
      return NextResponse.json(
        { detail: 'Invalid email/username or password' },
        { status: 401 }
      )
    }

    // Create JWT token
    const token = jwt.sign(
      { sub: user.id.toString() },
      'secret-key',
      { expiresIn: '24h' }
    )

    // Return user data without password
    const { password: _, ...userWithoutPassword } = user

    return NextResponse.json({
      access_token: token,
      token_type: 'bearer',
      user: userWithoutPassword
    })

  } catch (error) {
    console.error('Login error:', error)
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
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}
