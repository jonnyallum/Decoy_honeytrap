import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

const SnapchatChat = () => {
  const navigate = useNavigate()

  return (
    <div className="h-screen bg-yellow-400 flex flex-col">
      <div className="p-4 flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="text-white hover:bg-yellow-500"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-white font-bold text-xl">Snapchat</h1>
        <div className="w-16"></div>
      </div>
      
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Snapchat Interface</h2>
          <p className="text-lg">Coming Soon...</p>
          <p className="mt-4 text-sm opacity-75">
            This platform interface is under development
          </p>
        </div>
      </div>
    </div>
  )
}

export default SnapchatChat

