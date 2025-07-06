import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState(30);
  const [loading, setLoading] = useState(false);
  const [realTimeData, setRealTimeData] = useState({});
  const [discoveryAnalytics, setDiscoveryAnalytics] = useState({});
  const [threatAnalytics, setThreatAnalytics] = useState({});
  const [platformPerformance, setPlatformPerformance] = useState({});
  const [comprehensiveReport, setComprehensiveReport] = useState({});
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [profiles, setProfiles] = useState([]);

  useEffect(() => {
    fetchRealTimeData();
    fetchProfiles();
    fetchAnalyticsData();
    
    // Set up real-time updates
    const interval = setInterval(fetchRealTimeData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchRealTimeData = async () => {
    try {
      const response = await fetch('/api/analytics/real-time-dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setRealTimeData(data);
    } catch (error) {
      console.error('Error fetching real-time data:', error);
    }
  };

  const fetchProfiles = async () => {
    try {
      const response = await fetch('/api/profiles', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setProfiles(data.profiles || []);
    } catch (error) {
      console.error('Error fetching profiles:', error);
    }
  };

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Fetch all analytics data
      const [discoveryRes, threatRes, performanceRes, reportRes] = await Promise.all([
        fetch(`/api/analytics/discovery-analytics?days=${timeRange}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
        }),
        fetch(`/api/analytics/threat-analytics?days=${timeRange}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
        }),
        fetch(`/api/analytics/platform-performance?days=${timeRange}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
        }),
        fetch(`/api/analytics/comprehensive-report?days=${timeRange}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
        })
      ]);

      const [discoveryData, threatData, performanceData, reportData] = await Promise.all([
        discoveryRes.json(),
        threatRes.json(),
        performanceRes.json(),
        reportRes.json()
      ]);

      setDiscoveryAnalytics(discoveryData.discovery_analytics || {});
      setThreatAnalytics(threatData.threat_analytics || {});
      setPlatformPerformance(performanceData.platform_performance || {});
      setComprehensiveReport(reportData);

    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (exportType = 'json') => {
    try {
      const response = await fetch('/api/analytics/export-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          export_type: exportType,
          days: timeRange,
          include_sections: ['discovery', 'threats', 'performance']
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Download the data as a file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `honeytrap-analytics-${timeRange}days-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('Analytics data exported successfully!');
      } else {
        alert('Error exporting data: ' + data.error);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Error exporting data');
    }
  };

  const OverviewTab = () => (
    <div className="analytics-overview">
      <div className="real-time-stats">
        <h3>Real-Time Status</h3>
        <div className="stats-grid">
          <div className="stat-card real-time">
            <h4>Recent Discoveries</h4>
            <div className="stat-number">{realTimeData.real_time_data?.recent_discoveries || 0}</div>
            <span className="stat-period">Last 24 hours</span>
          </div>
          <div className="stat-card real-time">
            <h4>Recent Threats</h4>
            <div className="stat-number">{realTimeData.real_time_data?.recent_threats || 0}</div>
            <span className="stat-period">Last 24 hours</span>
          </div>
          <div className="stat-card real-time">
            <h4>Active Sessions</h4>
            <div className="stat-number">{realTimeData.real_time_data?.active_sessions?.total_active || 0}</div>
            <span className="stat-period">Currently active</span>
          </div>
          <div className="stat-card alert">
            <h4>High Risk Sessions</h4>
            <div className="stat-number">{realTimeData.alerts?.high_risk_sessions || 0}</div>
            <span className="stat-period">Requires attention</span>
          </div>
        </div>
      </div>

      <div className="executive-summary">
        <h3>Executive Summary ({timeRange} days)</h3>
        <div className="summary-grid">
          <div className="summary-card">
            <h4>Total Discoveries</h4>
            <div className="summary-number">{comprehensiveReport.executive_summary?.total_discoveries || 0}</div>
          </div>
          <div className="summary-card">
            <h4>Threat Events</h4>
            <div className="summary-number">{comprehensiveReport.executive_summary?.total_threat_events || 0}</div>
          </div>
          <div className="summary-card">
            <h4>Conversion Rate</h4>
            <div className="summary-number">{comprehensiveReport.executive_summary?.threat_conversion_rate || 0}%</div>
          </div>
          <div className="summary-card">
            <h4>High Risk Sessions</h4>
            <div className="summary-number">{comprehensiveReport.executive_summary?.high_risk_sessions || 0}</div>
          </div>
        </div>
      </div>

      <div className="key-insights">
        <h3>Key Insights</h3>
        <div className="insights-list">
          {(comprehensiveReport.key_insights || []).map((insight, index) => (
            <div key={index} className="insight-item">
              <span className="insight-icon">💡</span>
              <span className="insight-text">{insight}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="recommendations">
        <h3>Recommendations</h3>
        <div className="recommendations-list">
          {(comprehensiveReport.recommendations || []).slice(0, 5).map((recommendation, index) => (
            <div key={index} className="recommendation-item">
              <span className="recommendation-icon">📋</span>
              <span className="recommendation-text">{recommendation}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const DiscoveryTab = () => (
    <div className="discovery-analytics">
      <div className="discovery-summary">
        <h3>Discovery Analytics ({timeRange} days)</h3>
        <div className="discovery-stats">
          <div className="stat-item">
            <span className="stat-label">Total Discoveries:</span>
            <span className="stat-value">{discoveryAnalytics.total_discoveries || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Unique Profiles:</span>
            <span className="stat-value">{discoveryAnalytics.unique_profiles || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Unique Sessions:</span>
            <span className="stat-value">{discoveryAnalytics.unique_sessions || 0}</span>
          </div>
        </div>
      </div>

      <div className="discovery-breakdown">
        <h4>Discovery Methods by Platform</h4>
        <div className="breakdown-table">
          <div className="table-header">
            <span>Platform</span>
            <span>Method</span>
            <span>Count</span>
            <span>Avg. Time</span>
          </div>
          {(discoveryAnalytics.discovery_breakdown || []).map((item, index) => (
            <div key={index} className="table-row">
              <span className="platform-name">{item.platform}</span>
              <span className="method-name">{item.method}</span>
              <span className="count-value">{item.count}</span>
              <span className="time-value">{item.avg_hours_ago}h ago</span>
            </div>
          ))}
        </div>
      </div>

      <div className="hourly-distribution">
        <h4>Discovery Pattern by Hour</h4>
        <div className="hourly-chart">
          {(discoveryAnalytics.hourly_distribution || []).map((item, index) => (
            <div key={index} className="hour-bar">
              <div 
                className="bar-fill" 
                style={{ 
                  height: `${(item.count / Math.max(...(discoveryAnalytics.hourly_distribution || []).map(h => h.count))) * 100}%` 
                }}
              ></div>
              <span className="hour-label">{item.hour}:00</span>
              <span className="hour-count">{item.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="geographic-distribution">
        <h4>Geographic Distribution</h4>
        <div className="geo-list">
          {(discoveryAnalytics.geographic_distribution || []).slice(0, 10).map((item, index) => (
            <div key={index} className="geo-item">
              <span className="geo-location">
                {item.location.city || 'Unknown'}, {item.location.country || 'Unknown'}
              </span>
              <span className="geo-count">{item.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ThreatTab = () => (
    <div className="threat-analytics">
      <div className="threat-summary">
        <h3>Threat Analytics ({timeRange} days)</h3>
      </div>

      <div className="threat-levels">
        <h4>Threat Level Distribution</h4>
        <div className="threat-level-chart">
          {(threatAnalytics.threat_level_distribution || []).map((item, index) => (
            <div key={index} className="threat-level-item">
              <span className={`threat-level level-${item.threat_level}`}>
                Level {item.threat_level}
              </span>
              <div className="threat-bar">
                <div 
                  className="threat-fill" 
                  style={{ 
                    width: `${(item.count / Math.max(...(threatAnalytics.threat_level_distribution || []).map(t => t.count))) * 100}%` 
                  }}
                ></div>
              </div>
              <span className="threat-count">{item.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="threat-indicators">
        <h4>Top Threat Indicators</h4>
        <div className="indicators-list">
          {(threatAnalytics.top_threat_indicators || []).slice(0, 8).map((item, index) => (
            <div key={index} className="indicator-item">
              <div className="indicator-header">
                <span className="indicator-name">{item.indicator.replace('_', ' ')}</span>
                <span className="indicator-count">{item.count}</span>
              </div>
              <div className="indicator-description">{item.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="high-risk-sessions">
        <h4>High Risk Sessions</h4>
        <div className="sessions-list">
          {(threatAnalytics.high_risk_sessions || []).slice(0, 10).map((session, index) => (
            <div key={index} className="session-item">
              <div className="session-header">
                <span className="session-id">Session: {session.session_id.substring(0, 8)}...</span>
                <span className={`risk-score score-${Math.floor(session.risk_score / 20)}`}>
                  Risk: {session.risk_score}%
                </span>
              </div>
              <div className="session-indicators">
                {session.threat_indicators.map((indicator, idx) => (
                  <span key={idx} className="session-indicator">{indicator}</span>
                ))}
              </div>
              <div className="session-time">{new Date(session.timestamp).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="platform-threats">
        <h4>Platform Threat Analysis</h4>
        <div className="platform-threat-table">
          <div className="table-header">
            <span>Platform</span>
            <span>Avg Threat Level</span>
            <span>Total Events</span>
            <span>High Threat Events</span>
            <span>Threat Rate</span>
          </div>
          {(threatAnalytics.platform_threat_analysis || []).map((platform, index) => (
            <div key={index} className="table-row">
              <span className="platform-name">{platform.platform}</span>
              <span className="threat-level">{platform.avg_threat_level}</span>
              <span className="total-events">{platform.total_events}</span>
              <span className="high-events">{platform.high_threat_events}</span>
              <span className="threat-rate">{platform.threat_rate}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const PlatformTab = () => (
    <div className="platform-analytics">
      <div className="platform-summary">
        <h3>Platform Performance ({timeRange} days)</h3>
      </div>

      <div className="platform-metrics">
        <h4>Platform Effectiveness</h4>
        <div className="metrics-grid">
          {(platformPerformance.platform_metrics || []).map((platform, index) => (
            <div key={index} className="platform-card">
              <div className="platform-header">
                <h5>{platform.platform.toUpperCase()}</h5>
                <span className={`effectiveness-score score-${Math.floor(platform.effectiveness_score / 20)}`}>
                  {platform.effectiveness_score}%
                </span>
              </div>
              
              <div className="platform-stats">
                <div className="stat-row">
                  <span>Views:</span>
                  <span>{platform.total_views}</span>
                </div>
                <div className="stat-row">
                  <span>Contacts:</span>
                  <span>{platform.total_contacts}</span>
                </div>
                <div className="stat-row">
                  <span>Engagements:</span>
                  <span>{platform.total_engagements}</span>
                </div>
                <div className="stat-row">
                  <span>Threats:</span>
                  <span>{platform.total_threats}</span>
                </div>
              </div>

              <div className="platform-rates">
                <div className="rate-item">
                  <span className="rate-label">Contact Rate:</span>
                  <span className="rate-value">{platform.contact_rate}%</span>
                </div>
                <div className="rate-item">
                  <span className="rate-label">Engagement Rate:</span>
                  <span className="rate-value">{platform.engagement_rate}%</span>
                </div>
                <div className="rate-item">
                  <span className="rate-label">Threat Rate:</span>
                  <span className="rate-value">{platform.threat_rate}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="platform-recommendations">
        <h4>Platform Recommendations</h4>
        <div className="recommendations-list">
          {(platformPerformance.recommendations || []).map((recommendation, index) => (
            <div key={index} className="recommendation-item">
              <span className="recommendation-icon">💡</span>
              <span className="recommendation-text">{recommendation}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ProfileTab = () => (
    <div className="profile-analytics">
      <div className="profile-selector">
        <h3>Profile Performance Analysis</h3>
        <select 
          value={selectedProfile?.id || ''} 
          onChange={(e) => {
            const profile = profiles.find(p => p.id === parseInt(e.target.value));
            setSelectedProfile(profile);
          }}
        >
          <option value="">Select a profile...</option>
          {profiles.map(profile => (
            <option key={profile.id} value={profile.id}>
              {profile.name} (@{profile.username}) - {profile.platform_type}
            </option>
          ))}
        </select>
      </div>

      {selectedProfile && (
        <ProfilePerformanceView profile={selectedProfile} timeRange={timeRange} />
      )}
    </div>
  );

  const ProfilePerformanceView = ({ profile, timeRange }) => {
    const [profileData, setProfileData] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
      fetchProfileData();
    }, [profile.id, timeRange]);

    const fetchProfileData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/analytics/profile-performance/${profile.id}?days=${timeRange}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
          }
        });
        const data = await response.json();
        setProfileData(data);
      } catch (error) {
        console.error('Error fetching profile data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (loading) {
      return <div className="loading">Loading profile data...</div>;
    }

    const performance = profileData.profile_performance || {};
    const discoveryData = performance.discovery_analytics || {};

    return (
      <div className="profile-performance">
        <div className="profile-info">
          <h4>{performance.profile_name} (@{performance.username})</h4>
          <div className="profile-details">
            <span>Platform: {performance.platform_type}</span>
            <span>Age: {performance.age}</span>
            <span>Status: {performance.status}</span>
          </div>
        </div>

        <div className="profile-metrics">
          <div className="metric-card">
            <h5>Discoveries</h5>
            <div className="metric-value">{discoveryData.total_discoveries || 0}</div>
          </div>
          <div className="metric-card">
            <h5>Unique Sessions</h5>
            <div className="metric-value">{discoveryData.unique_sessions || 0}</div>
          </div>
          <div className="metric-card">
            <h5>Unique Profiles</h5>
            <div className="metric-value">{discoveryData.unique_profiles || 0}</div>
          </div>
        </div>

        <div className="profile-recommendations">
          <h5>Recommendations</h5>
          <div className="recommendations-list">
            {(profileData.recommendations || []).map((recommendation, index) => (
              <div key={index} className="recommendation-item">
                <span className="recommendation-text">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <div className="header-left">
          <h2>Analytics Dashboard</h2>
          <div className="time-range-selector">
            <label>Time Range:</label>
            <select value={timeRange} onChange={(e) => setTimeRange(parseInt(e.target.value))}>
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>
        
        <div className="header-actions">
          <button onClick={() => fetchAnalyticsData()} className="refresh-btn" disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
          <button onClick={() => exportData('json')} className="export-btn">
            Export Data
          </button>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'discovery' ? 'active' : ''}
          onClick={() => setActiveTab('discovery')}
        >
          Discovery Analytics
        </button>
        <button 
          className={activeTab === 'threats' ? 'active' : ''}
          onClick={() => setActiveTab('threats')}
        >
          Threat Analytics
        </button>
        <button 
          className={activeTab === 'platforms' ? 'active' : ''}
          onClick={() => setActiveTab('platforms')}
        >
          Platform Performance
        </button>
        <button 
          className={activeTab === 'profiles' ? 'active' : ''}
          onClick={() => setActiveTab('profiles')}
        >
          Profile Analysis
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'discovery' && <DiscoveryTab />}
        {activeTab === 'threats' && <ThreatTab />}
        {activeTab === 'platforms' && <PlatformTab />}
        {activeTab === 'profiles' && <ProfileTab />}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Loading analytics data...</div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;

