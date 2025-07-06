import React, { useState, useEffect } from 'react';
import './ContentManagement.css';

const ContentManagement = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [automationStatus, setAutomationStatus] = useState({});
  const [contentStats, setContentStats] = useState({});
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [scheduledContent, setScheduledContent] = useState([]);
  const [contentTemplates, setContentTemplates] = useState({});
  const [postingPatterns, setPostingPatterns] = useState({});
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentCalendar, setContentCalendar] = useState(null);

  useEffect(() => {
    fetchAutomationStatus();
    fetchProfiles();
    fetchContentTemplates();
    fetchPostingPatterns();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      fetchScheduledContent(selectedProfile.id);
    }
  }, [selectedProfile]);

  const fetchAutomationStatus = async () => {
    try {
      const response = await fetch('/api/content-automation/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setAutomationStatus(data.automation_status || {});
      setContentStats(data.content_statistics || {});
    } catch (error) {
      console.error('Error fetching automation status:', error);
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

  const fetchScheduledContent = async (profileId) => {
    try {
      const response = await fetch(`/api/content-automation/scheduled-content/${profileId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setScheduledContent(data.scheduled_content || []);
    } catch (error) {
      console.error('Error fetching scheduled content:', error);
    }
  };

  const fetchContentTemplates = async () => {
    try {
      const response = await fetch('/api/content-automation/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setContentTemplates(data.templates || {});
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchPostingPatterns = async () => {
    try {
      const response = await fetch('/api/content-automation/posting-patterns', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      setPostingPatterns(data.posting_patterns || {});
    } catch (error) {
      console.error('Error fetching posting patterns:', error);
    }
  };

  const startAutomation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/content-automation/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        alert('Automation service started successfully!');
        fetchAutomationStatus();
      } else {
        alert('Error starting automation: ' + data.error);
      }
    } catch (error) {
      console.error('Error starting automation:', error);
      alert('Error starting automation');
    } finally {
      setLoading(false);
    }
  };

  const stopAutomation = async () => {
    if (!confirm('Are you sure you want to stop the automation service?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/content-automation/stop', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        alert('Automation service stopped successfully!');
        fetchAutomationStatus();
      } else {
        alert('Error stopping automation: ' + data.error);
      }
    } catch (error) {
      console.error('Error stopping automation:', error);
      alert('Error stopping automation');
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async (profileId, contentType = null) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/content-automation/generate-content/${profileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ content_type: contentType })
      });
      const data = await response.json();
      if (response.ok) {
        setGeneratedContent(data.content);
        alert('Content generated successfully!');
      } else {
        alert('Error generating content: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating content:', error);
      alert('Error generating content');
    } finally {
      setLoading(false);
    }
  };

  const generateContentCalendar = async (profileId, days = 30) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/content-automation/generate-calendar/${profileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ days })
      });
      const data = await response.json();
      if (response.ok) {
        setContentCalendar(data.calendar);
        alert(`Content calendar generated for ${days} days!`);
      } else {
        alert('Error generating calendar: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating calendar:', error);
      alert('Error generating calendar');
    } finally {
      setLoading(false);
    }
  };

  const autoScheduleCalendar = async (profileId, calendarData) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/content-automation/auto-schedule-calendar/${profileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ calendar: calendarData })
      });
      const data = await response.json();
      if (response.ok) {
        alert(`Auto-scheduled ${data.result.scheduled_count} content items!`);
        fetchScheduledContent(profileId);
        setContentCalendar(null);
      } else {
        alert('Error auto-scheduling: ' + data.error);
      }
    } catch (error) {
      console.error('Error auto-scheduling:', error);
      alert('Error auto-scheduling');
    } finally {
      setLoading(false);
    }
  };

  const emergencyStop = async () => {
    if (!confirm('Are you sure you want to perform an emergency stop? This will stop all automation and cancel all scheduled content.')) {
      return;
    }

    const reason = prompt('Please provide a reason for the emergency stop:');
    if (!reason) return;

    setLoading(true);
    try {
      const response = await fetch('/api/content-automation/emergency-stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ reason })
      });
      const data = await response.json();
      if (response.ok) {
        alert(`Emergency stop completed. ${data.cancelled_content_count} content items cancelled.`);
        fetchAutomationStatus();
        if (selectedProfile) {
          fetchScheduledContent(selectedProfile.id);
        }
      } else {
        alert('Error in emergency stop: ' + data.error);
      }
    } catch (error) {
      console.error('Error in emergency stop:', error);
      alert('Error in emergency stop');
    } finally {
      setLoading(false);
    }
  };

  const deleteScheduledContent = async (contentId) => {
    if (!confirm('Are you sure you want to delete this scheduled content?')) {
      return;
    }

    try {
      const response = await fetch(`/api/content-automation/content/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      if (response.ok) {
        alert('Content deleted successfully!');
        if (selectedProfile) {
          fetchScheduledContent(selectedProfile.id);
        }
      } else {
        const data = await response.json();
        alert('Error deleting content: ' + data.error);
      }
    } catch (error) {
      console.error('Error deleting content:', error);
      alert('Error deleting content');
    }
  };

  const OverviewTab = () => (
    <div className="content-overview">
      <div className="automation-status">
        <h3>Automation Service Status</h3>
        <div className="status-grid">
          <div className="status-card">
            <h4>Service Status</h4>
            <div className={`status-indicator ${automationStatus.is_running ? 'running' : 'stopped'}`}>
              {automationStatus.is_running ? 'Running' : 'Stopped'}
            </div>
            <div className="status-actions">
              {automationStatus.is_running ? (
                <button onClick={stopAutomation} className="stop-btn" disabled={loading}>
                  Stop Service
                </button>
              ) : (
                <button onClick={startAutomation} className="start-btn" disabled={loading}>
                  Start Service
                </button>
              )}
              <button onClick={emergencyStop} className="emergency-btn" disabled={loading}>
                Emergency Stop
              </button>
            </div>
          </div>
          
          <div className="status-card">
            <h4>Scheduler Status</h4>
            <div className={`status-indicator ${automationStatus.scheduler_active ? 'active' : 'inactive'}`}>
              {automationStatus.scheduler_active ? 'Active' : 'Inactive'}
            </div>
            <p>Scheduled Jobs: {automationStatus.scheduled_jobs || 0}</p>
          </div>
        </div>
      </div>

      <div className="content-statistics">
        <h3>Content Statistics</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Total Content</h4>
            <div className="stat-number">{contentStats.total_content || 0}</div>
          </div>
          <div className="stat-card">
            <h4>Posted Content</h4>
            <div className="stat-number">{contentStats.posted_content || 0}</div>
          </div>
          <div className="stat-card">
            <h4>Scheduled Content</h4>
            <div className="stat-number">{contentStats.scheduled_content || 0}</div>
          </div>
          <div className="stat-card">
            <h4>Success Rate</h4>
            <div className="stat-number">{(contentStats.success_rate || 0).toFixed(1)}%</div>
          </div>
        </div>

        <div className="platform-breakdown">
          <h4>Platform Breakdown</h4>
          <div className="platform-stats">
            {Object.entries(contentStats.platform_breakdown || {}).map(([platform, count]) => (
              <div key={platform} className="platform-stat">
                <span className="platform-name">{platform}</span>
                <span className="platform-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const ContentGenerationTab = () => (
    <div className="content-generation">
      <div className="profile-selector">
        <h3>Select Profile</h3>
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
        <div className="generation-controls">
          <div className="profile-info">
            <h4>{selectedProfile.name} (@{selectedProfile.username})</h4>
            <p>Platform: {selectedProfile.platform_type} | Age: {selectedProfile.age}</p>
            <p>Interests: {selectedProfile.interests ? JSON.parse(selectedProfile.interests).join(', ') : 'None'}</p>
          </div>

          <div className="generation-actions">
            <h4>Content Generation</h4>
            <div className="action-buttons">
              <button 
                onClick={() => generateContent(selectedProfile.id)}
                disabled={loading}
                className="generate-btn"
              >
                Generate Single Content
              </button>
              <button 
                onClick={() => generateContentCalendar(selectedProfile.id, 7)}
                disabled={loading}
                className="calendar-btn"
              >
                Generate 7-Day Calendar
              </button>
              <button 
                onClick={() => generateContentCalendar(selectedProfile.id, 30)}
                disabled={loading}
                className="calendar-btn"
              >
                Generate 30-Day Calendar
              </button>
            </div>
          </div>

          {generatedContent && (
            <div className="generated-content">
              <h4>Generated Content</h4>
              <div className="content-preview">
                <p><strong>Type:</strong> {generatedContent.content_type}</p>
                <p><strong>Platform:</strong> {generatedContent.platform_type}</p>
                <p><strong>Content:</strong> {generatedContent.content_text}</p>
                {generatedContent.hashtags && generatedContent.hashtags.length > 0 && (
                  <p><strong>Hashtags:</strong> {generatedContent.hashtags.join(' ')}</p>
                )}
                <p><strong>Suggested Time:</strong> {generatedContent.suggested_posting_time}</p>
                <p><strong>Engagement Prediction:</strong> {generatedContent.engagement_prediction?.engagement_level}</p>
                <p><strong>Risk Level:</strong> {generatedContent.risk_assessment?.risk_level}</p>
              </div>
              <button 
                onClick={() => {
                  // Schedule this content
                  const scheduleTime = new Date();
                  scheduleTime.setHours(parseInt(generatedContent.suggested_posting_time.split(':')[0]));
                  scheduleTime.setMinutes(parseInt(generatedContent.suggested_posting_time.split(':')[1]));
                  
                  fetch(`/api/content-automation/schedule-content/${selectedProfile.id}`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify({
                      content_data: generatedContent,
                      schedule_time: scheduleTime.toISOString()
                    })
                  }).then(response => {
                    if (response.ok) {
                      alert('Content scheduled successfully!');
                      fetchScheduledContent(selectedProfile.id);
                      setGeneratedContent(null);
                    }
                  });
                }}
                className="schedule-btn"
              >
                Schedule This Content
              </button>
            </div>
          )}

          {contentCalendar && (
            <div className="content-calendar">
              <h4>Generated Content Calendar</h4>
              <div className="calendar-info">
                <p><strong>Period:</strong> {contentCalendar.calendar_period}</p>
                <p><strong>Total Posts:</strong> {contentCalendar.total_posts}</p>
                <p><strong>Average Posts/Day:</strong> {contentCalendar.average_posts_per_day.toFixed(1)}</p>
              </div>
              
              <div className="calendar-preview">
                <h5>Preview (First 5 items):</h5>
                {contentCalendar.calendar.slice(0, 5).map((item, index) => (
                  <div key={index} className="calendar-item">
                    <span className="date">{item.date} {item.time}</span>
                    <span className="content">{item.content.content_text}</span>
                    <span className="type">{item.content.content_type}</span>
                  </div>
                ))}
                {contentCalendar.calendar.length > 5 && (
                  <p>... and {contentCalendar.calendar.length - 5} more items</p>
                )}
              </div>

              <div className="calendar-actions">
                <button 
                  onClick={() => autoScheduleCalendar(selectedProfile.id, contentCalendar.calendar)}
                  disabled={loading}
                  className="auto-schedule-btn"
                >
                  Auto-Schedule All Content
                </button>
                <button 
                  onClick={() => setContentCalendar(null)}
                  className="cancel-btn"
                >
                  Cancel Calendar
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const ScheduledContentTab = () => (
    <div className="scheduled-content">
      <div className="profile-selector">
        <h3>Select Profile</h3>
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
        <div className="content-list">
          <div className="list-header">
            <h4>Scheduled Content for {selectedProfile.name}</h4>
            <p>Total items: {scheduledContent.length}</p>
          </div>

          <div className="content-items">
            {scheduledContent.length === 0 ? (
              <div className="no-content">
                <p>No scheduled content found for this profile.</p>
                <button 
                  onClick={() => generateContentCalendar(selectedProfile.id, 7)}
                  className="generate-btn"
                >
                  Generate Content Calendar
                </button>
              </div>
            ) : (
              scheduledContent.map(item => (
                <div key={item.id} className="content-item">
                  <div className="content-header">
                    <span className="content-type">{item.content_type}</span>
                    <span className={`content-status ${item.status}`}>{item.status}</span>
                    <span className="scheduled-time">
                      {new Date(item.scheduled_time).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="content-text">
                    {item.content_text}
                  </div>
                  
                  <div className="content-actions">
                    {item.status === 'scheduled' && (
                      <button 
                        onClick={() => deleteScheduledContent(item.id)}
                        className="delete-btn"
                      >
                        Delete
                      </button>
                    )}
                    {item.status === 'posted' && (
                      <div className="engagement-stats">
                        <span>Likes: {item.likes_count}</span>
                        <span>Comments: {item.comments_count}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );

  const TemplatesTab = () => (
    <div className="templates-view">
      <h3>Content Templates</h3>
      
      <div className="templates-grid">
        {Object.entries(contentTemplates).map(([platform, platformData]) => (
          <div key={platform} className="platform-templates">
            <h4>{platform.toUpperCase()}</h4>
            
            {Object.entries(platformData).map(([ageGroup, ageData]) => (
              <div key={ageGroup} className="age-group-templates">
                <h5>Age Group: {ageGroup}</h5>
                
                {Object.entries(ageData).map(([contentType, templates]) => (
                  <div key={contentType} className="content-type-templates">
                    <h6>{contentType}</h6>
                    <div className="template-list">
                      {templates.slice(0, 3).map((template, index) => (
                        <div key={index} className="template-item">
                          {template}
                        </div>
                      ))}
                      {templates.length > 3 && (
                        <div className="template-count">
                          +{templates.length - 3} more templates
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="posting-patterns">
        <h3>Posting Patterns</h3>
        <div className="patterns-grid">
          {Object.entries(postingPatterns).map(([platform, pattern]) => (
            <div key={platform} className="pattern-card">
              <h4>{platform.toUpperCase()}</h4>
              <p><strong>Frequency:</strong> {pattern.frequency}</p>
              <p><strong>Peak Times:</strong> {pattern.peak_times?.join(', ')}</p>
              <p><strong>Response Likelihood:</strong> {(pattern.response_likelihood * 100).toFixed(0)}%</p>
              
              <div className="content-mix">
                <strong>Content Mix:</strong>
                {Object.entries(pattern.content_mix || {}).map(([type, percentage]) => (
                  <div key={type} className="mix-item">
                    <span>{type}: {percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="content-management">
      <div className="management-header">
        <h2>Content Management & Automation</h2>
        <div className="header-status">
          <span className={`service-status ${automationStatus.is_running ? 'running' : 'stopped'}`}>
            Service: {automationStatus.is_running ? 'Running' : 'Stopped'}
          </span>
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
          className={activeTab === 'generation' ? 'active' : ''}
          onClick={() => setActiveTab('generation')}
        >
          Content Generation
        </button>
        <button 
          className={activeTab === 'scheduled' ? 'active' : ''}
          onClick={() => setActiveTab('scheduled')}
        >
          Scheduled Content
        </button>
        <button 
          className={activeTab === 'templates' ? 'active' : ''}
          onClick={() => setActiveTab('templates')}
        >
          Templates & Patterns
        </button>
      </div>

      <div className="management-content">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'generation' && <ContentGenerationTab />}
        {activeTab === 'scheduled' && <ScheduledContentTab />}
        {activeTab === 'templates' && <TemplatesTab />}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Processing...</div>
        </div>
      )}
    </div>
  );
};

export default ContentManagement;

