// Centralized data import resolver for all API routes
// This ensures consistent imports across all API endpoints regardless of their depth

import { users, mentors, getConnections, addConnection, getMessages, addMessage, getSessions, addSession } from '../data/shared'

// Re-export all data functions for consistent access
export {
  users,
  mentors,
  getConnections,
  addConnection,
  getMessages,
  addMessage,
  getSessions,
  addSession
}

// Type definitions for better IDE support
export type User = typeof users[0]
export type Mentor = typeof mentors[0]
export type Connection = ReturnType<typeof getConnections>[0]
export type Message = ReturnType<typeof getMessages>[0]
export type Session = ReturnType<typeof getSessions>[0]
