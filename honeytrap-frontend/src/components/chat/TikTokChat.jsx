import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

const TikTokChat = () => {
  const navigate = useNavigate()

  return (
    <div className="h-screen bg-black flex flex-col">
      <div className="p-4 flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="text-white hover:bg-gray-800"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-white font-bold text-xl">TikTok</h1>
        <div className="w-16"></div>
      </div>
      
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-white">
          <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent">
            TikTok Interface
          </h2>
          <p className="text-lg">Coming Soon...</p>
          <p className="mt-4 text-sm opacity-75">
            This platform interface is under development
          </p>
        </div>
      </div>
    </div>
  )
}

export default TikTokChat

