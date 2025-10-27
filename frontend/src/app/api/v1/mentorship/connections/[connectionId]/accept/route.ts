// Vercel serverless function for accepting mentorship connections
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { users, getConnections } from '../../../../../../../data/shared'

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

export async function POST(request: NextRequest, { params }: { params: { connectionId: string } }) {
  try {
    const authHeader = request.headers.get('authorization')
    const currentUser = getCurrentUser(authHeader || '')
    
    if (!currentUser) {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const connectionId = parseInt(params.connectionId)
    const connections = getConnections()
    const connection = connections.find(c => c.id === connectionId)

    if (!connection) {
      return NextResponse.json(
        { detail: 'Connection not found' },
        { status: 404 }
      )
    }

    // Check if current user is the mentor for this connection
    if (connection.mentor_id !== currentUser.id) {
      return NextResponse.json(
        { detail: 'Unauthorized - only the mentor can accept this connection' },
        { status: 403 }
      )
    }

    // Update connection status to active
    connection.status = 'active'
    connection.updated_at = new Date().toISOString()

    return NextResponse.json({
      success: true,
      message: 'Connection request accepted successfully',
      connection: connection
    })

  } catch (error) {
    console.error('Accept connection error:', error)
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

