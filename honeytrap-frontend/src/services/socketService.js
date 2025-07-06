import { io } from 'socket.io-client'

class SocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.eventListeners = new Map()
  }

  connect(serverUrl = 'http://localhost:5002') {
    if (this.socket && this.isConnected) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      this.socket = io(serverUrl, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true
      })

      this.socket.on('connect', () => {
        console.log('Connected to WebSocket server')
        this.isConnected = true
        resolve()
      })

      this.socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket server')
        this.isConnected = false
      })

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        this.isConnected = false
        reject(error)
      })

      this.socket.on('error', (error) => {
        console.error('WebSocket error:', error)
      })

      // Set up event forwarding
      this.setupEventForwarding()
    })
  }

  setupEventForwarding() {
    const events = [
      'connected',
      'chat_joined',
      'message_received',
      'typing_start',
      'typing_stop',
      'high_risk_alert',
      'admin_joined',
      'session_stats',
      'error'
    ]

    events.forEach(event => {
      this.socket.on(event, (data) => {
        this.notifyListeners(event, data)
      })
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
      this.eventListeners.clear()
    }
  }

  // Chat methods
  joinChat(platformType) {
    if (!this.isConnected) {
      throw new Error('Not connected to server')
    }
    this.socket.emit('join_chat', { platform_type: platformType })
  }

  sendMessage(sessionId, message) {
    if (!this.isConnected) {
      throw new Error('Not connected to server')
    }
    this.socket.emit('send_message', { session_id: sessionId, message })
  }

  // Admin methods
  joinAdmin() {
    if (!this.isConnected) {
      throw new Error('Not connected to server')
    }
    this.socket.emit('join_admin')
  }

  // Event listener management
  addEventListener(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event).add(callback)

    // Return unsubscribe function
    return () => {
      const listeners = this.eventListeners.get(event)
      if (listeners) {
        listeners.delete(callback)
        if (listeners.size === 0) {
          this.eventListeners.delete(event)
        }
      }
    }
  }

  removeEventListener(event, callback) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
      if (listeners.size === 0) {
        this.eventListeners.delete(event)
      }
    }
  }

  notifyListeners(event, data) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error)
        }
      })
    }
  }

  // Utility methods
  isSocketConnected() {
    return this.isConnected && this.socket && this.socket.connected
  }

  getSocketId() {
    return this.socket ? this.socket.id : null
  }
}

// Create singleton instance
const socketService = new SocketService()

export default socketService

