// Vercel serverless function for messages
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

const connections = [
  {
    id: 1,
    mentor_id: 1,
    mentee_id: 2,
    status: 'active',
  }
]

let messages = [
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

let messageIdCounter = 3

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

    const connectionMessages = messages
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
      id: messageIdCounter++,
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

    messages.push(newMessage)

    return NextResponse.json({
      success: true,
      message: 'Message sent successfully',
      data: newMessage
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
