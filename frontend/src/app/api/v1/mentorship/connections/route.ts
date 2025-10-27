// Vercel serverless function for mentorship connections
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { users, getConnections } from '../../../../../../frontend/src/data/shared'

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
    const connections = getConnections()
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
