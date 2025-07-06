import React, { useState, useEffect } from 'react';
import './ProfileManagement.css';

const ProfileManagement = () => {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [deploymentStrategies, setDeploymentStrategies] = useState({});
  const [platformAnalytics, setPlatformAnalytics] = useState({});

  // Fetch initial data
  useEffect(() => {
    fetchProfiles();
    fetchStats();
    fetchDeploymentStrategies();
    fetchPlatformAnalytics();
  }, []);

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

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/profiles/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchDeploymentStrategies = async () => {
    try {
      const response = await fetch('/api/profile-management/deployment-strategies', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setDeploymentStrategies(data);
    } catch (error) {
      console.error('Error fetching deployment strategies:', error);
    }
  };

  const fetchPlatformAnalytics = async () => {
    try {
      const response = await fetch('/api/profile-management/platform-analytics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setPlatformAnalytics(data);
    } catch (error) {
      console.error('Error fetching platform analytics:', error);
    }
  };

  const createComprehensiveProfile = async (platformType, strategy) => {
    setLoading(true);
    try {
      const response = await fetch('/api/profile-management/create-comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          platform_type: platformType,
          deployment_strategy: strategy
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert('Comprehensive profile created successfully!');
        fetchProfiles();
        setSelectedProfile(data.data.profile);
      } else {
        alert('Error creating profile: ' + data.error);
      }
    } catch (error) {
      console.error('Error creating profile:', error);
      alert('Error creating profile');
    } finally {
      setLoading(false);
    }
  };

  const batchDeployProfiles = async (count, platforms, strategy) => {
    setLoading(true);
    try {
      const response = await fetch('/api/profile-management/batch-deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          count: count,
          platforms: platforms,
          strategy: strategy
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert(`Batch deployment completed! Success rate: ${data.results.deployment_summary.success_rate}%`);
        fetchProfiles();
      } else {
        alert('Error in batch deployment: ' + data.error);
      }
    } catch (error) {
      console.error('Error in batch deployment:', error);
      alert('Error in batch deployment');
    } finally {
      setLoading(false);
    }
  };

  const generateProfileImages = async (profileId, gender) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/profile-management/generate-images/${profileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ gender })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert('Profile images generated successfully!');
        fetchProfiles();
      } else {
        alert('Error generating images: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating images:', error);
      alert('Error generating images');
    } finally {
      setLoading(false);
    }
  };

  const emergencyShutdown = async (profileIds, reason) => {
    if (!confirm('Are you sure you want to perform an emergency shutdown? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/profile-management/emergency-shutdown', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          profile_ids: profileIds,
          reason: reason
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert(`Emergency shutdown completed for ${data.shutdown_results.length} profiles`);
        fetchProfiles();
      } else {
        alert('Error in emergency shutdown: ' + data.error);
      }
    } catch (error) {
      console.error('Error in emergency shutdown:', error);
      alert('Error in emergency shutdown');
    } finally {
      setLoading(false);
    }
  };

  const ProfileOverview = () => (
    <div className="profile-overview">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Profiles</h3>
          <div className="stat-number">{stats.total_profiles || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Deployed Profiles</h3>
          <div className="stat-number">{stats.deployed_profiles || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Active Profiles</h3>
          <div className="stat-number">{stats.active_profiles || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Total Contacts</h3>
          <div className="stat-number">{stats.total_contacts || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Evidence Captured</h3>
          <div className="stat-number">{stats.total_evidence || 0}</div>
        </div>
      </div>

      <div className="platform-breakdown">
        <h3>Platform Distribution</h3>
        <div className="platform-stats">
          {Object.entries(stats.platform_breakdown || {}).map(([platform, count]) => (
            <div key={platform} className="platform-stat">
              <span className="platform-name">{platform}</span>
              <span className="platform-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Profiles</h3>
        <div className="profile-list">
          {profiles.slice(0, 5).map(profile => (
            <div key={profile.id} className="profile-item" onClick={() => setSelectedProfile(profile)}>
              <div className="profile-info">
                <span className="profile-name">{profile.name}</span>
                <span className="profile-platform">{profile.platform_type}</span>
                <span className={`profile-status ${profile.status}`}>{profile.status}</span>
              </div>
              <div className="profile-metrics">
                <span>Contacts: {profile.contact_attempts}</span>
                <span>Evidence: {profile.evidence_captured}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ProfileCreation = () => {
    const [newProfilePlatform, setNewProfilePlatform] = useState('discord');
    const [newProfileStrategy, setNewProfileStrategy] = useState('standard');
    const [batchCount, setBatchCount] = useState(3);
    const [batchPlatforms, setBatchPlatforms] = useState(['discord', 'instagram']);
    const [batchStrategy, setBatchStrategy] = useState('standard');

    return (
      <div className="profile-creation">
        <div className="creation-section">
          <h3>Create Single Profile</h3>
          <div className="form-group">
            <label>Platform:</label>
            <select value={newProfilePlatform} onChange={(e) => setNewProfilePlatform(e.target.value)}>
              <option value="discord">Discord</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="snapchat">Snapchat</option>
              <option value="tiktok">TikTok</option>
            </select>
          </div>
          <div className="form-group">
            <label>Deployment Strategy:</label>
            <select value={newProfileStrategy} onChange={(e) => setNewProfileStrategy(e.target.value)}>
              {Object.entries(deploymentStrategies.strategies || {}).map(([key, strategy]) => (
                <option key={key} value={key}>{strategy.name}</option>
              ))}
            </select>
          </div>
          <button 
            onClick={() => createComprehensiveProfile(newProfilePlatform, newProfileStrategy)}
            disabled={loading}
            className="create-btn"
          >
            {loading ? 'Creating...' : 'Create Comprehensive Profile'}
          </button>
        </div>

        <div className="creation-section">
          <h3>Batch Deployment</h3>
          <div className="form-group">
            <label>Number of Profiles:</label>
            <input 
              type="number" 
              value={batchCount} 
              onChange={(e) => setBatchCount(parseInt(e.target.value))}
              min="1" 
              max="10"
            />
          </div>
          <div className="form-group">
            <label>Platforms:</label>
            <div className="checkbox-group">
              {['discord', 'instagram', 'facebook', 'snapchat', 'tiktok'].map(platform => (
                <label key={platform}>
                  <input 
                    type="checkbox" 
                    checked={batchPlatforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setBatchPlatforms([...batchPlatforms, platform]);
                      } else {
                        setBatchPlatforms(batchPlatforms.filter(p => p !== platform));
                      }
                    }}
                  />
                  {platform}
                </label>
              ))}
            </div>
          </div>
          <div className="form-group">
            <label>Strategy:</label>
            <select value={batchStrategy} onChange={(e) => setBatchStrategy(e.target.value)}>
              {Object.entries(deploymentStrategies.strategies || {}).map(([key, strategy]) => (
                <option key={key} value={key}>{strategy.name}</option>
              ))}
            </select>
          </div>
          <button 
            onClick={() => batchDeployProfiles(batchCount, batchPlatforms, batchStrategy)}
            disabled={loading || batchPlatforms.length === 0}
            className="create-btn"
          >
            {loading ? 'Deploying...' : 'Batch Deploy Profiles'}
          </button>
        </div>

        <div className="strategy-info">
          <h3>Deployment Strategies</h3>
          {Object.entries(deploymentStrategies.strategies || {}).map(([key, strategy]) => (
            <div key={key} className="strategy-card">
              <h4>{strategy.name}</h4>
              <p>{strategy.description}</p>
              <div className="strategy-details">
                <span>Activity: {strategy.activity_level}</span>
                <span>Posting: {strategy.posting_frequency}</span>
                <span>Risk: {strategy.risk_level}</span>
                <span>Timeline: {strategy.expected_timeline}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const ProfileList = () => {
    const [filter, setFilter] = useState('all');
    const [sortBy, setSortBy] = useState('created_at');

    const filteredProfiles = profiles.filter(profile => {
      if (filter === 'all') return true;
      return profile.status === filter || profile.platform_type === filter;
    });

    const sortedProfiles = filteredProfiles.sort((a, b) => {
      if (sortBy === 'created_at') return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === 'contacts') return b.contact_attempts - a.contact_attempts;
      if (sortBy === 'evidence') return b.evidence_captured - a.evidence_captured;
      return 0;
    });

    return (
      <div className="profile-list-view">
        <div className="list-controls">
          <div className="filter-group">
            <label>Filter:</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Profiles</option>
              <option value="created">Created</option>
              <option value="deployed">Deployed</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="discord">Discord</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="snapchat">Snapchat</option>
              <option value="tiktok">TikTok</option>
            </select>
          </div>
          <div className="sort-group">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="created_at">Created Date</option>
              <option value="contacts">Contact Attempts</option>
              <option value="evidence">Evidence Captured</option>
            </select>
          </div>
        </div>

        <div className="profiles-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Platform</th>
                <th>Age</th>
                <th>Status</th>
                <th>Contacts</th>
                <th>Evidence</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedProfiles.map(profile => (
                <tr key={profile.id} onClick={() => setSelectedProfile(profile)}>
                  <td>{profile.name}</td>
                  <td>{profile.platform_type}</td>
                  <td>{profile.age}</td>
                  <td><span className={`status ${profile.status}`}>{profile.status}</span></td>
                  <td>{profile.contact_attempts}</td>
                  <td>{profile.evidence_captured}</td>
                  <td>{new Date(profile.created_at).toLocaleDateString()}</td>
                  <td>
                    <button onClick={(e) => {
                      e.stopPropagation();
                      generateProfileImages(profile.id, 'female');
                    }}>
                      Generate Images
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        emergencyShutdown([profile.id], 'Manual shutdown');
                      }}
                      className="danger-btn"
                    >
                      Shutdown
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const ProfileDetails = () => {
    if (!selectedProfile) {
      return <div className="no-selection">Select a profile to view details</div>;
    }

    return (
      <div className="profile-details">
        <div className="profile-header">
          <h3>{selectedProfile.name} (@{selectedProfile.username})</h3>
          <span className={`status ${selectedProfile.status}`}>{selectedProfile.status}</span>
        </div>

        <div className="profile-info-grid">
          <div className="info-section">
            <h4>Basic Information</h4>
            <p><strong>Age:</strong> {selectedProfile.age}</p>
            <p><strong>Platform:</strong> {selectedProfile.platform_type}</p>
            <p><strong>Location:</strong> {selectedProfile.location}</p>
            <p><strong>Bio:</strong> {selectedProfile.bio}</p>
          </div>

          <div className="info-section">
            <h4>Interests</h4>
            <div className="interests-list">
              {selectedProfile.interests.map((interest, index) => (
                <span key={index} className="interest-tag">{interest}</span>
              ))}
            </div>
          </div>

          <div className="info-section">
            <h4>Performance Metrics</h4>
            <p><strong>Contact Attempts:</strong> {selectedProfile.contact_attempts}</p>
            <p><strong>Successful Engagements:</strong> {selectedProfile.successful_engagements}</p>
            <p><strong>Evidence Captured:</strong> {selectedProfile.evidence_captured}</p>
            <p><strong>Last Activity:</strong> {selectedProfile.last_activity ? new Date(selectedProfile.last_activity).toLocaleString() : 'Never'}</p>
          </div>

          <div className="info-section">
            <h4>Deployment Information</h4>
            <p><strong>Created:</strong> {new Date(selectedProfile.created_at).toLocaleString()}</p>
            <p><strong>Deployed:</strong> {selectedProfile.deployment_date ? new Date(selectedProfile.deployment_date).toLocaleString() : 'Not deployed'}</p>
            <p><strong>Platform ID:</strong> {selectedProfile.platform_profile_id || 'Not set'}</p>
            <p><strong>Profile URL:</strong> {selectedProfile.profile_url || 'Not set'}</p>
          </div>
        </div>

        <div className="profile-actions">
          <button onClick={() => generateProfileImages(selectedProfile.id, 'female')}>
            Generate Images
          </button>
          <button onClick={() => {
            // Implement content calendar view
            alert('Content calendar feature coming soon');
          }}>
            View Content Calendar
          </button>
          <button onClick={() => {
            // Implement performance report
            alert('Performance report feature coming soon');
          }}>
            Performance Report
          </button>
          <button 
            onClick={() => emergencyShutdown([selectedProfile.id], 'Manual shutdown')}
            className="danger-btn"
          >
            Emergency Shutdown
          </button>
        </div>

        <div className="backstory-section">
          <h4>Operational Backstory</h4>
          <div className="backstory-text">
            {selectedProfile.backstory}
          </div>
        </div>
      </div>
    );
  };

  const Analytics = () => (
    <div className="analytics-view">
      <div className="analytics-header">
        <h3>Platform Analytics</h3>
        <p>Period: {platformAnalytics.period || '30 days'}</p>
      </div>

      <div className="overall-stats">
        <h4>Overall Statistics</h4>
        <div className="stats-grid">
          <div className="stat-card">
            <h5>Total Profiles</h5>
            <div className="stat-number">{platformAnalytics.overall_stats?.total_profiles || 0}</div>
          </div>
          <div className="stat-card">
            <h5>Total Contacts</h5>
            <div className="stat-number">{platformAnalytics.overall_stats?.total_contacts || 0}</div>
          </div>
          <div className="stat-card">
            <h5>Total Evidence</h5>
            <div className="stat-number">{platformAnalytics.overall_stats?.total_evidence || 0}</div>
          </div>
          <div className="stat-card">
            <h5>Average Effectiveness</h5>
            <div className="stat-number">{(platformAnalytics.overall_stats?.average_effectiveness || 0).toFixed(1)}%</div>
          </div>
        </div>
      </div>

      <div className="platform-breakdown-analytics">
        <h4>Platform Breakdown</h4>
        <div className="platform-analytics-grid">
          {Object.entries(platformAnalytics.platform_breakdown || {}).map(([platform, data]) => (
            <div key={platform} className="platform-analytics-card">
              <h5>{platform.toUpperCase()}</h5>
              <div className="platform-metrics">
                <p>Profiles: {data.total_profiles}</p>
                <p>Views: {data.recent_views}</p>
                <p>Contacts: {data.recent_contacts}</p>
                <p>Threats: {data.recent_threats}</p>
                <p>Effectiveness: {data.effectiveness_rate.toFixed(1)}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recommendations">
        <h4>Recommendations</h4>
        <ul>
          {(platformAnalytics.recommendations || []).map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );

  return (
    <div className="profile-management">
      <div className="management-header">
        <h2>Profile Management System</h2>
        <div className="header-actions">
          <button 
            onClick={() => emergencyShutdown(profiles.filter(p => p.status === 'active').map(p => p.id), 'Mass emergency shutdown')}
            className="emergency-btn"
            disabled={loading}
          >
            Emergency Shutdown All
          </button>
        </div>
      </div>

      <div className="management-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'creation' ? 'active' : ''}
          onClick={() => setActiveTab('creation')}
        >
          Profile Creation
        </button>
        <button 
          className={activeTab === 'list' ? 'active' : ''}
          onClick={() => setActiveTab('list')}
        >
          Profile List
        </button>
        <button 
          className={activeTab === 'details' ? 'active' : ''}
          onClick={() => setActiveTab('details')}
        >
          Profile Details
        </button>
        <button 
          className={activeTab === 'analytics' ? 'active' : ''}
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </div>

      <div className="management-content">
        {activeTab === 'overview' && <ProfileOverview />}
        {activeTab === 'creation' && <ProfileCreation />}
        {activeTab === 'list' && <ProfileList />}
        {activeTab === 'details' && <ProfileDetails />}
        {activeTab === 'analytics' && <Analytics />}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Processing...</div>
        </div>
      )}
    </div>
  );
};

export default ProfileManagement;

