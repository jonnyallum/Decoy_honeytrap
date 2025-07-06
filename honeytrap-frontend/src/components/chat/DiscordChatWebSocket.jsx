import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Send, Hash, Users, Settings, Mic, Headphones } from 'lucide-react'
import socketService from '../../services/socketService'

const DiscordChatWebSocket = () => {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [persona, setPersona] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    initializeWebSocket()
    return () => {
      socketService.disconnect()
    }
  }, [])

  const initializeWebSocket = async () => {
    try {
      setConnectionError(null)
      await socketService.connect('http://localhost:5002')
      setIsConnected(true)

      // Set up event listeners
      const unsubscribers = [
        socketService.addEventListener('connected', handleConnected),
        socketService.addEventListener('chat_joined', handleChatJoined),
        socketService.addEventListener('message_received', handleMessageReceived),
        socketService.addEventListener('typing_start', handleTypingStart),
        socketService.addEventListener('typing_stop', handleTypingStop),
        socketService.addEventListener('error', handleError)
      ]

      // Join chat session
      socketService.joinChat('discord')

      // Cleanup function
      return () => {
        unsubscribers.forEach(unsub => unsub())
      }
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error)
      setConnectionError('Failed to connect to chat server. Please try again.')
      setIsConnected(false)
    }
  }

  const handleConnected = (data) => {
    console.log('WebSocket connected:', data)
  }

  const handleChatJoined = (data) => {
    console.log('Chat joined:', data)
    setSessionId(data.session_id)
    setPersona(data.persona)
    
    // Add initial greeting message
    const greetingMessage = {
      id: Date.now(),
      sender_type: 'decoy',
      message_content: data.greeting,
      timestamp: new Date().toISOString()
    }
    setMessages([greetingMessage])
  }

  const handleMessageReceived = (message) => {
    console.log('Message received:', message)
    setMessages(prev => [...prev, message])
  }

  const handleTypingStart = (data) => {
    console.log('Typing started:', data)
    setIsTyping(true)
  }

  const handleTypingStop = () => {
    console.log('Typing stopped')
    setIsTyping(false)
  }

  const handleError = (error) => {
    console.error('WebSocket error:', error)
    setConnectionError(error.message || 'An error occurred')
  }

  const sendMessage = () => {
    if (!newMessage.trim() || !sessionId || !isConnected) return

    try {
      socketService.sendMessage(sessionId, newMessage)
      setNewMessage('')
    } catch (error) {
      console.error('Failed to send message:', error)
      setConnectionError('Failed to send message. Please check your connection.')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const retryConnection = () => {
    setConnectionError(null)
    initializeWebSocket()
  }

  if (connectionError) {
    return (
      <div className="h-screen bg-gray-800 text-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-4">Connection Error</h2>
          <p className="text-gray-300 mb-4">{connectionError}</p>
          <div className="space-x-4">
            <Button onClick={retryConnection} className="bg-blue-600 hover:bg-blue-700">
              Retry Connection
            </Button>
            <Button onClick={() => navigate('/')} variant="outline">
              Back to Platform Selection
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!isConnected || !sessionId) {
    return (
      <div className="h-screen bg-gray-800 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-lg">Connecting to chat server...</p>
          <p className="text-sm text-gray-400 mt-2">Establishing secure connection</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-gray-800 text-white flex">
      {/* Sidebar */}
      <div className="w-60 bg-gray-900 flex flex-col">
        {/* Server Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-white">Gaming Community</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/')}
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </div>
          <div className="text-xs text-green-400 mt-1 flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            WebSocket Connected
          </div>
        </div>

        {/* Channels */}
        <div className="flex-1 p-2">
          <div className="mb-4">
            <div className="flex items-center text-gray-400 text-xs font-semibold uppercase tracking-wide mb-2">
              <Hash className="w-3 h-3 mr-1" />
              Text Channels
            </div>
            <div className="space-y-1">
              <div className="flex items-center px-2 py-1 rounded bg-gray-700 text-white">
                <Hash className="w-4 h-4 mr-2 text-gray-400" />
                <span className="text-sm">general</span>
              </div>
              <div className="flex items-center px-2 py-1 rounded text-gray-400 hover:bg-gray-700 hover:text-white cursor-pointer">
                <Hash className="w-4 h-4 mr-2" />
                <span className="text-sm">gaming</span>
              </div>
              <div className="flex items-center px-2 py-1 rounded text-gray-400 hover:bg-gray-700 hover:text-white cursor-pointer">
                <Hash className="w-4 h-4 mr-2" />
                <span className="text-sm">random</span>
              </div>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-center text-gray-400 text-xs font-semibold uppercase tracking-wide mb-2">
              <Users className="w-3 h-3 mr-1" />
              Online - 3
            </div>
            <div className="space-y-2">
              {persona && (
                <div className="flex items-center px-2 py-1">
                  <div className="relative">
                    <Avatar className="w-6 h-6">
                      <AvatarFallback className="bg-green-500 text-white text-xs">
                        {persona.name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></div>
                  </div>
                  <span className="ml-2 text-sm text-white">{persona.name}</span>
                  <Badge variant="secondary" className="ml-auto text-xs">
                    {persona.age}
                  </Badge>
                </div>
              )}
              <div className="flex items-center px-2 py-1">
                <div className="relative">
                  <Avatar className="w-6 h-6">
                    <AvatarFallback className="bg-blue-500 text-white text-xs">A</AvatarFallback>
                  </Avatar>
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></div>
                </div>
                <span className="ml-2 text-sm text-gray-300">Alex_Gaming</span>
              </div>
              <div className="flex items-center px-2 py-1">
                <div className="relative">
                  <Avatar className="w-6 h-6">
                    <AvatarFallback className="bg-purple-500 text-white text-xs">M</AvatarFallback>
                  </Avatar>
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-gray-900"></div>
                </div>
                <span className="ml-2 text-sm text-gray-300">Mike_2024</span>
              </div>
            </div>
          </div>
        </div>

        {/* User Panel */}
        <div className="p-2 bg-gray-800 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-gray-600 text-white">U</AvatarFallback>
              </Avatar>
              <div className="ml-2">
                <div className="text-sm font-medium">You</div>
                <div className="text-xs text-gray-400">#1234</div>
              </div>
            </div>
            <div className="flex space-x-1">
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0 text-gray-400 hover:text-white">
                <Mic className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0 text-gray-400 hover:text-white">
                <Headphones className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0 text-gray-400 hover:text-white">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4">
          <Hash className="w-5 h-5 text-gray-400 mr-2" />
          <span className="font-semibold">general</span>
          <div className="ml-4 text-sm text-gray-400">
            Real-time chat with WebSocket connection
          </div>
          <div className="ml-auto text-xs text-green-400">
            Live Connection Active
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="flex items-start space-x-3 hover:bg-gray-700/30 p-2 rounded">
              <Avatar className="w-10 h-10">
                <AvatarFallback className={`text-white ${
                  message.sender_type === 'decoy' ? 'bg-green-500' : 'bg-blue-500'
                }`}>
                  {message.sender_type === 'decoy' ? persona?.name[0] : 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium text-white">
                    {message.sender_type === 'decoy' ? persona?.name : 'You'}
                  </span>
                  {message.sender_type === 'decoy' && (
                    <Badge variant="secondary" className="text-xs">
                      {persona?.age}
                    </Badge>
                  )}
                  <span className="text-xs text-gray-400">
                    {formatTime(message.timestamp)}
                  </span>
                  {message.threat_level > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      Alert Level {message.threat_level}
                    </Badge>
                  )}
                </div>
                <div className="text-gray-100">
                  {message.message_content}
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex items-start space-x-3 p-2">
              <Avatar className="w-10 h-10">
                <AvatarFallback className="bg-green-500 text-white">
                  {persona?.name[0]}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium text-white">{persona?.name}</span>
                  <span className="text-xs text-gray-400">is typing...</span>
                </div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="p-4 bg-gray-800">
          <div className="flex items-center space-x-2">
            <div className="flex-1 relative">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message #general"
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-400 pr-12"
                disabled={!isConnected}
              />
              <Button
                onClick={sendMessage}
                disabled={!newMessage.trim() || !isConnected}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 p-0 bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {isConnected ? 'Connected via WebSocket' : 'Connecting...'}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DiscordChatWebSocket

