import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Send, Hash, Users, Settings, Mic, Headphones } from 'lucide-react'

const DiscordChat = () => {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [persona, setPersona] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize chat session
    initializeChat()
  }, [])

  const initializeChat = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ platform_type: 'discord' })
      })
      
      const data = await response.json()
      if (data.status === 'success') {
        setSessionId(data.session_id)
        setPersona(data.persona)
        
        // Add initial greeting message
        const greetingMessage = {
          id: Date.now(),
          sender_type: 'decoy',
          message_content: getRandomGreeting(data.persona),
          timestamp: new Date().toISOString()
        }
        setMessages([greetingMessage])
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error)
    }
  }

  const getRandomGreeting = (persona) => {
    const greetings = persona?.response_patterns?.greeting || ['hey!', 'hi there!', 'what\'s up?']
    return greetings[Math.floor(Math.random() * greetings.length)]
  }

  const sendMessage = async () => {
    if (!newMessage.trim() || !sessionId) return

    const userMessage = {
      id: Date.now(),
      sender_type: 'user',
      message_content: newMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setIsTyping(true)

    try {
      const response = await fetch('http://localhost:5001/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: newMessage
        })
      })

      const data = await response.json()
      
      // Simulate typing delay
      setTimeout(() => {
        setIsTyping(false)
        
        if (data.status === 'success') {
          const aiMessage = {
            id: Date.now() + 1,
            sender_type: 'decoy',
            message_content: data.response,
            timestamp: new Date().toISOString(),
            threat_level: data.threat_level
          }
          setMessages(prev => [...prev, aiMessage])
        }
      }, 1000 + Math.random() * 2000) // Random delay between 1-3 seconds
      
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsTyping(false)
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
            General discussion and chat
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
                  <span className="text-xs text-gray-400">typing...</span>
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
              />
              <Button
                onClick={sendMessage}
                disabled={!newMessage.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 p-0 bg-blue-600 hover:bg-blue-700"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DiscordChat

