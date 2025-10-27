// Vercel serverless function for mentorship connect
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { users, getConnections, addConnection } from '../../../../data/shared'

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

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    const currentUser = getCurrentUser(authHeader || '')
    
    if (!currentUser) {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const formData = await request.formData()
    const mentor_id = parseInt(formData.get('mentor_id') as string)
    const message = formData.get('connection_message') as string
    const goals = (formData.get('goals') as string || '').split(',').filter(g => g.trim())
    const target_band_score = parseFloat(formData.get('target_band_score') as string || '7.5')
    const focus_areas = (formData.get('focus_areas') as string || '').split(',').filter(f => f.trim())

    // Find mentor
    const mentor = users.find(u => u.id === mentor_id)
    if (!mentor) {
      return NextResponse.json(
        { detail: 'Mentor not found' },
        { status: 404 }
      )
    }

    // Check if connection already exists
    const connections = getConnections()
    const existingConnection = connections.find(
      conn => conn.mentor_id === mentor_id && conn.mentee_id === currentUser.id
    )
    
    if (existingConnection) {
      return NextResponse.json(
        { detail: 'Connection request already exists' },
        { status: 400 }
      )
    }

    // Create new connection
    const newConnection = {
      mentor_id,
      mentee_id: currentUser.id,
      status: 'pending',
      connection_message: message,
      goals,
      target_band_score,
      focus_areas,
      created_at: new Date().toISOString(),
      mentor,
      mentee: currentUser
    }

    const savedConnection = addConnection(newConnection)

    return NextResponse.json({
      success: true,
      message: 'Connection request sent successfully',
      connection: savedConnection
    })

  } catch (error) {
    console.error('Connect error:', error)
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
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
