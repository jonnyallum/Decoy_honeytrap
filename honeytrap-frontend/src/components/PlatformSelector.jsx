import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MessageCircle, Camera, Music } from 'lucide-react'

const PlatformSelector = () => {
  const navigate = useNavigate()
  const [selectedPlatform, setSelectedPlatform] = useState(null)

  const platforms = [
    {
      id: 'discord',
      name: 'Discord',
      description: 'Chat with gamers and communities',
      icon: MessageCircle,
      color: 'bg-indigo-600 hover:bg-indigo-700',
      textColor: 'text-indigo-600'
    },
    {
      id: 'snapchat',
      name: 'Snapchat',
      description: 'Share moments with friends',
      icon: Camera,
      color: 'bg-yellow-400 hover:bg-yellow-500',
      textColor: 'text-yellow-600'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      description: 'Discover and create videos',
      icon: Music,
      color: 'bg-pink-600 hover:bg-pink-700',
      textColor: 'text-pink-600'
    }
  ]

  const handlePlatformSelect = (platformId) => {
    setSelectedPlatform(platformId)
    // Add a small delay for visual feedback
    setTimeout(() => {
      navigate(`/${platformId}`)
    }, 300)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Platform
          </h1>
          <p className="text-xl text-gray-600">
            Connect with friends and discover new communities
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {platforms.map((platform) => {
            const IconComponent = platform.icon
            const isSelected = selectedPlatform === platform.id
            
            return (
              <Card 
                key={platform.id}
                className={`cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl ${
                  isSelected ? 'ring-4 ring-blue-500 scale-105' : ''
                }`}
                onClick={() => handlePlatformSelect(platform.id)}
              >
                <CardHeader className="text-center pb-4">
                  <div className={`mx-auto w-16 h-16 rounded-full ${platform.color} flex items-center justify-center mb-4 transition-all duration-300`}>
                    <IconComponent className="w-8 h-8 text-white" />
                  </div>
                  <CardTitle className={`text-2xl font-bold ${platform.textColor}`}>
                    {platform.name}
                  </CardTitle>
                  <CardDescription className="text-gray-600">
                    {platform.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <Button 
                    className={`w-full ${platform.color} text-white transition-all duration-300`}
                    disabled={isSelected}
                  >
                    {isSelected ? 'Connecting...' : `Enter ${platform.name}`}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-gray-500">
            Safe and secure platform for connecting with others
          </p>
        </div>
      </div>
    </div>
  )
}

export default PlatformSelector

