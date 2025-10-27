// Vercel serverless function for deleting mentorship connections
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { users, getConnections } from '../../../../../../data/shared'

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

export async function DELETE(request: NextRequest, { params }: { params: { connectionId: string } }) {
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
    const connectionIndex = connections.findIndex(c => c.id === connectionId)

    if (connectionIndex === -1) {
      return NextResponse.json(
        { detail: 'Connection not found' },
        { status: 404 }
      )
    }

    const connection = connections[connectionIndex]

    // Check if current user is part of this connection
    if (connection.mentor_id !== currentUser.id && connection.mentee_id !== currentUser.id) {
      return NextResponse.json(
        { detail: 'Unauthorized - you can only delete your own connections' },
        { status: 403 }
      )
    }

    // Remove the connection
    connections.splice(connectionIndex, 1)

    return NextResponse.json({
      success: true,
      message: 'Connection deleted successfully'
    })

  } catch (error) {
    console.error('Delete connection error:', error)
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
      'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
