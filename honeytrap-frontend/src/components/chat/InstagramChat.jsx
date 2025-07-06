import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card } from '../ui/card';

const InstagramChat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'emma_t_13',
      content: 'heyy! saw your story, looks fun! 📸✨',
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
        sender: 'emma_t_13',
        content: generateAIResponse(newMessage),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isUser: false,
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face'
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1800);
  };

  const generateAIResponse = (userMessage) => {
    const responses = [
      "omggg thank you!! 💕 what have you been up to?",
      "aww you're so sweet! 🥺 love making new friends on here",
      "yasss! i'm always posting random stuff lol 📱",
      "haha thanks! i'm so bored rn, wanna chat? 💭",
      "you seem really cool! what kind of content do you post? 🤔",
      "ugh school is so boring, at least i have insta to keep me entertained 😅"
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Instagram Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="text-gray-700 hover:bg-gray-100 p-2"
          >
            ←
          </Button>
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face"
              alt="Emma"
              className="w-10 h-10 rounded-full border-2 border-transparent bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500 p-0.5"
            />
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">emma_t_13</h2>
            <p className="text-gray-500 text-sm">Active now</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="ghost" size="sm" className="text-gray-700 hover:bg-gray-100 p-2">
            📞
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-700 hover:bg-gray-100 p-2">
            📹
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-700 hover:bg-gray-100 p-2">
            ℹ️
          </Button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-white">
        <div className="max-w-4xl mx-auto space-y-3">
          {/* Profile Info */}
          <div className="text-center py-6">
            <div className="relative inline-block">
              <img
                src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=80&h=80&fit=crop&crop=face"
                alt="Emma"
                className="w-20 h-20 rounded-full border-4 border-transparent bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500 p-1"
              />
            </div>
            <h3 className="font-semibold text-lg mt-3">emma_t_13</h3>
            <p className="text-gray-500 text-sm">Emma Thompson • Instagram</p>
            <Button className="mt-3 bg-blue-500 hover:bg-blue-600 text-white px-6 py-1 rounded-lg text-sm">
              View Profile
            </Button>
          </div>

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} items-end space-x-2`}
            >
              {!message.isUser && (
                <img
                  src={message.avatar}
                  alt={message.sender}
                  className="w-6 h-6 rounded-full"
                />
              )}
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  message.isUser
                    ? 'bg-blue-500 text-white rounded-br-md'
                    : 'bg-gray-100 text-gray-800 rounded-bl-md border border-gray-200'
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
                className="w-6 h-6 rounded-full"
              />
              <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl rounded-bl-md border border-gray-200">
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
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <Button type="button" variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100 p-2">
              📷
            </Button>
            <div className="flex-1 relative">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Message..."
                className="w-full rounded-full border-gray-300 bg-gray-50 px-4 py-2 focus:bg-white focus:border-gray-400 focus:ring-0"
              />
            </div>
            <Button type="button" variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100 p-2">
              🎤
            </Button>
            <Button type="button" variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100 p-2">
              😊
            </Button>
            <Button type="button" variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100 p-2">
              ❤️
            </Button>
            {newMessage.trim() && (
              <Button
                type="submit"
                className="text-blue-500 hover:text-blue-600 font-semibold bg-transparent hover:bg-transparent p-0"
              >
                Send
              </Button>
            )}
          </div>
        </form>
      </div>

      {/* Instagram Stories Bar */}
      <div className="bg-white border-t border-gray-200 p-3">
        <div className="flex space-x-3 overflow-x-auto">
          <div className="flex flex-col items-center space-y-1 min-w-0">
            <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500 p-0.5">
              <img
                src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=48&h=48&fit=crop&crop=face"
                alt="Emma's Story"
                className="w-full h-full rounded-full border-2 border-white"
              />
            </div>
            <span className="text-xs text-gray-600 truncate">Your story</span>
          </div>
          <div className="flex flex-col items-center space-y-1 min-w-0">
            <div className="w-12 h-12 rounded-full bg-gray-300 p-0.5">
              <div className="w-full h-full rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500 text-xs">+</span>
              </div>
            </div>
            <span className="text-xs text-gray-600 truncate">Add story</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstagramChat;

