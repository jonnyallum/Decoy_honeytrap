import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'

// Import components
import PlatformSelector from './components/PlatformSelector'
import DiscordChat from './components/chat/DiscordChat'
import DiscordChatWebSocket from './components/chat/DiscordChatWebSocket'
import FacebookChat from './components/chat/FacebookChat'
import InstagramChat from './components/chat/InstagramChat'
import SnapchatChat from './components/chat/SnapchatChat'
import TikTokChat from './components/chat/TikTokChat'
import AdminDashboard from './components/admin/AdminDashboard'
import AdminLogin from './components/admin/AdminLogin'

function App() {
  const [isAdmin, setIsAdmin] = useState(false)

  // Check if user is accessing admin routes
  useEffect(() => {
    const path = window.location.pathname
    if (path.startsWith('/admin')) {
      setIsAdmin(true)
    }
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public decoy chat routes */}
          <Route path="/" element={<PlatformSelector />} />
          <Route path="/discord" element={<DiscordChat />} />
          <Route path="/discord-ws" element={<DiscordChatWebSocket />} />
          <Route path="/facebook" element={<FacebookChat />} />
          <Route path="/instagram" element={<InstagramChat />} />
          <Route path="/snapchat" element={<SnapchatChat />} />
          <Route path="/tiktok" element={<TikTokChat />} />
          
          {/* Admin routes */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

