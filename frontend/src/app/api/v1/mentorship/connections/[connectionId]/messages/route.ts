// Vercel serverless function for messages
import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { users, getConnections, getMessages, addMessage } from '../../../../../../data/shared'

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

export async function GET(
  request: NextRequest,
  { params }: { params: { connectionId: string } }
) {
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
    const connection = connections.find(conn => conn.id === connectionId)
    
    if (!connection) {
      return NextResponse.json(
        { detail: 'Connection not found' },
        { status: 404 }
      )
    }

    // Check if user has access to this connection
    if (connection.mentor_id !== currentUser.id && connection.mentee_id !== currentUser.id) {
      return NextResponse.json(
        { detail: 'Access denied' },
        { status: 403 }
      )
    }

    const connectionMessages = getMessages()
      .filter(msg => msg.connection_id === connectionId)
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())

    return NextResponse.json({
      success: true,
      messages: connectionMessages
    })

  } catch (error) {
    console.error('Get messages error:', error)
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { connectionId: string } }
) {
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
    const connection = connections.find(conn => conn.id === connectionId)
    
    if (!connection) {
      return NextResponse.json(
        { detail: 'Connection not found' },
        { status: 404 }
      )
    }

    // Check if user has access to this connection
    if (connection.mentor_id !== currentUser.id && connection.mentee_id !== currentUser.id) {
      return NextResponse.json(
        { detail: 'Access denied' },
        { status: 403 }
      )
    }

    const formData = await request.formData()
    const content = formData.get('content') as string
    const message_type = (formData.get('message_type') as string) || 'text'

    if (!content) {
      return NextResponse.json(
        { detail: 'Message content required' },
        { status: 400 }
      )
    }

    const newMessage = {
      connection_id: connectionId,
      sender_id: currentUser.id,
      message_type,
      content,
      file_url: null,
      file_name: null,
      file_size: null,
      is_read: false,
      read_at: null,
      is_edited: false,
      edited_at: null,
      created_at: new Date().toISOString(),
      sender: currentUser
    }

    const addedMessage = addMessage(newMessage)

    return NextResponse.json({
      success: true,
      message: 'Message sent successfully',
      data: addedMessage
    })

  } catch (error) {
    console.error('Send message error:', error)
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
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}

