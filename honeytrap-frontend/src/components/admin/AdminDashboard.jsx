import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ProfileManagement from './ProfileManagement'
import ContentManagement from './ContentManagement'
import AnalyticsDashboard from './AnalyticsDashboard'
import SocialAccountManager from './SocialAccountManager'
import { 
  Shield, 
  Users, 
  AlertTriangle, 
  FileText, 
  Activity,
  LogOut,
  Download,
  Eye,
  Clock,
  UserPlus,
  Calendar,
  BarChart3
} from 'lucide-react'

const AdminDashboard = () => {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    active_sessions: 0,
    total_sessions: 0,
    high_risk_sessions: 0,
    evidence_count: 0
  })
  const [sessions, setSessions] = useState([])
  const [recentHighRisk, setRecentHighRisk] = useState([])

  useEffect(() => {
    fetchDashboardData()
    // Set up polling for real-time updates
    const interval = setInterval(fetchDashboardData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/admin/dashboard')
      const data = await response.json()
      setStats(data.stats)
      setRecentHighRisk(data.recent_high_risk)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/admin/sessions')
      const data = await response.json()
      setSessions(data.sessions)
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    }
  }

  const generateReport = async (sessionId) => {
    try {
      const response = await fetch(`http://localhost:5001/api/admin/sessions/${sessionId}/report`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `evidence_report_${sessionId}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Failed to generate report:', error)
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getEscalationBadge = (level) => {
    if (level >= 2) return <Badge variant="destructive">High Risk</Badge>
    if (level >= 1) return <Badge variant="secondary">Suspicious</Badge>
    return <Badge variant="outline">Normal</Badge>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Honeytrap Network</h1>
                <p className="text-sm text-gray-600">Hampshire Police - Admin Dashboard</p>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={() => navigate('/admin')}
              className="flex items-center"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.active_sessions}</div>
              <p className="text-xs text-muted-foreground">Currently online</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_sessions}</div>
              <p className="text-xs text-muted-foreground">Last 30 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.high_risk_sessions}</div>
              <p className="text-xs text-muted-foreground">Requiring attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Evidence Collected</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.evidence_count}</div>
              <p className="text-xs text-muted-foreground">Digital evidence packets</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="recent" className="space-y-4">
          <TabsList>
            <TabsTrigger value="recent">Recent High-Risk Sessions</TabsTrigger>
            <TabsTrigger value="sessions" onClick={fetchSessions}>All Sessions</TabsTrigger>
            <TabsTrigger value="profiles">Profile Management</TabsTrigger>
            <TabsTrigger value="content">Content Management</TabsTrigger>
            <TabsTrigger value="analytics">Analytics Dashboard</TabsTrigger>
            <TabsTrigger value="social-accounts">Social Accounts</TabsTrigger>
          </TabsList>

          <TabsContent value="recent" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent High-Risk Sessions</CardTitle>
                <CardDescription>
                  Sessions that have triggered escalation alerts
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentHighRisk.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No high-risk sessions detected recently
                  </div>
                ) : (
                  <div className="space-y-4">
                    {recentHighRisk.map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="font-medium">Session {session.session_id.slice(0, 8)}...</span>
                            {getEscalationBadge(session.escalation_level)}
                            {session.evidence_captured && (
                              <Badge variant="outline" className="text-blue-600">
                                Evidence Captured
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>IP: {session.user_ip}</div>
                            <div className="flex items-center">
                              <Clock className="w-3 h-3 mr-1" />
                              Last Activity: {formatTime(session.last_activity)}
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {/* View session details */}}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                          {session.evidence_captured && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => generateReport(session.id)}
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Report
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sessions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>All Sessions</CardTitle>
                <CardDescription>
                  Complete list of chat sessions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {sessions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No sessions found
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sessions.map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="font-medium">Session {session.session_id.slice(0, 8)}...</span>
                            {getEscalationBadge(session.escalation_level)}
                          </div>
                          <div className="text-sm text-gray-600">
                            <div>IP: {session.user_ip}</div>
                            <div>Created: {formatTime(session.created_at)}</div>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profiles" className="space-y-4">
            <ProfileManagement />
          </TabsContent>

          <TabsContent value="content" className="space-y-4">
            <ContentManagement />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <AnalyticsDashboard />
          </TabsContent>

          <TabsContent value="social-accounts" className="space-y-4">
            <SocialAccountManager />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default AdminDashboard

