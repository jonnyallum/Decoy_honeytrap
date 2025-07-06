import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card } from '../ui/card';

const FacebookChat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'Emma Thompson',
      content: 'Hey! 👋 How are you doing?',
      timestamp: '2:15 PM',
      isUser: false,
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face'
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      sender: 'You',
      content: newMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      setIsTyping(false);
      const aiResponse = {
        id: messages.length + 2,
        sender: 'Emma Thompson',
        content: generateAIResponse(newMessage),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isUser: false,
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face'
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 2000);
  };

  const generateAIResponse = (userMessage) => {
    const responses = [
      "That's cool! I love chatting with new people 😊",
      "Haha yeah! What kind of stuff are you into?",
      "OMG really? That sounds awesome! 🎉",
      "I'm just hanging out at home, pretty bored tbh 😅",
      "What's your favorite thing to do for fun?",
      "Nice! I wish I had more friends to talk to like this 💭"
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Facebook Header */}
      <div className="bg-[#1877f2] text-white p-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="text-white hover:bg-blue-600 p-2"
          >
            ←
          </Button>
          <img
            src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face"
            alt="Emma"
            className="w-10 h-10 rounded-full border-2 border-white"
          />
          <div>
            <h2 className="font-semibold text-lg">Emma Thompson</h2>
            <p className="text-blue-100 text-sm">Active now</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600 p-2">
            📞
          </Button>
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600 p-2">
            📹
          </Button>
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600 p-2">
            ℹ️
          </Button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} items-end space-x-2`}
            >
              {!message.isUser && (
                <img
                  src={message.avatar}
                  alt={message.sender}
                  className="w-8 h-8 rounded-full"
                />
              )}
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  message.isUser
                    ? 'bg-[#1877f2] text-white rounded-br-md'
                    : 'bg-gray-200 text-gray-800 rounded-bl-md'
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start items-end space-x-2">
              <img
                src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face"
                alt="Emma"
                className="w-8 h-8 rounded-full"
              />
              <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-2xl rounded-bl-md">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <Button type="button" variant="ghost" size="sm" className="text-[#1877f2] hover:bg-blue-50 p-2">
              📎
            </Button>
            <Button type="button" variant="ghost" size="sm" className="text-[#1877f2] hover:bg-blue-50 p-2">
              📷
            </Button>
            <div className="flex-1 relative">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                className="w-full rounded-full border-gray-300 bg-gray-100 px-4 py-2 focus:bg-white focus:border-[#1877f2] focus:ring-[#1877f2]"
              />
            </div>
            <Button type="button" variant="ghost" size="sm" className="text-[#1877f2] hover:bg-blue-50 p-2">
              😊
            </Button>
            <Button
              type="submit"
              disabled={!newMessage.trim()}
              className="bg-[#1877f2] hover:bg-blue-600 text-white rounded-full p-2 disabled:opacity-50"
            >
              ➤
            </Button>
          </div>
        </form>
      </div>

      {/* Facebook Messenger Footer */}
      <div className="bg-gray-100 text-center py-2 text-xs text-gray-500">
        <p>End-to-end encrypted • Facebook Messenger</p>
      </div>
    </div>
  );
};

export default FacebookChat;

