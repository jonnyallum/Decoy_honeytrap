import React, { useState, useEffect } from 'react';
import './SocialAccountManager.css';

const SocialAccountManager = () => {
  const [accounts, setAccounts] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [loginMethod, setLoginMethod] = useState('oauth');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState({});

  // Login form state
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
    email: '',
    displayName: ''
  });

  useEffect(() => {
    loadAccounts();
    loadPlatforms();
    loadStats();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await fetch('/api/accounts');
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
      setError('Failed to load accounts');
    }
  };

  const loadPlatforms = async () => {
    try {
      const response = await fetch('/api/auth/platforms');
      if (response.ok) {
        const data = await response.json();
        setPlatforms(data.platforms || []);
      }
    } catch (error) {
      console.error('Error loading platforms:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleOAuthLogin = async (platform) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/auth/oauth/${platform}`);
      
      if (response.ok) {
        const data = await response.json();
        // Open OAuth URL in new window
        const authWindow = window.open(
          data.auth_url,
          'oauth_login',
          'width=600,height=700,scrollbars=yes,resizable=yes'
        );

        // Poll for window closure
        const pollTimer = setInterval(() => {
          if (authWindow.closed) {
            clearInterval(pollTimer);
            setLoading(false);
            loadAccounts(); // Refresh accounts list
            setShowLoginModal(false);
            setSuccess(`Successfully connected to ${platform}`);
          }
        }, 1000);
      } else {
        throw new Error('Failed to start OAuth process');
      }
    } catch (error) {
      setLoading(false);
      setError(`OAuth login failed: ${error.message}`);
    }
  };

  const handleCredentialLogin = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/auth/credentials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform: selectedPlatform,
          username: loginForm.username,
          password: loginForm.password,
          email: loginForm.email,
          display_name: loginForm.displayName
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Successfully logged into ${selectedPlatform}`);
        setShowLoginModal(false);
        setLoginForm({ username: '', password: '', email: '', displayName: '' });
        loadAccounts();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Login failed');
      }
    } catch (error) {
      setError(`Credential login failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async (accountId) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/accounts/${accountId}/logout`, {
        method: 'POST',
      });

      if (response.ok) {
        setSuccess('Account logged out successfully');
        loadAccounts();
      } else {
        throw new Error('Logout failed');
      }
    } catch (error) {
      setError(`Logout failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshTokens = async (accountId) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/accounts/${accountId}/refresh`, {
        method: 'POST',
      });

      if (response.ok) {
        setSuccess('Tokens refreshed successfully');
        loadAccounts();
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      setError(`Token refresh failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (accountId) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/accounts/${accountId}/test`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.valid) {
        setSuccess('Connection test successful');
      } else {
        setError(`Connection test failed: ${data.error}`);
      }
    } catch (error) {
      setError(`Connection test failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSuccess('Account deleted successfully');
        loadAccounts();
        setSelectedAccount(null);
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      setError(`Delete failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#4CAF50';
      case 'inactive': return '#9E9E9E';
      case 'error': return '#F44336';
      case 'suspended': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: '📘',
      instagram: '📷',
      twitter: '🐦',
      discord: '💬',
      tiktok: '🎵',
      snapchat: '👻',
      linkedin: '💼',
      youtube: '📺'
    };
    return icons[platform] || '🌐';
  };

  return (
    <div className="social-account-manager">
      <div className="header">
        <h2>Social Media Account Management</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowLoginModal(true)}
        >
          Add Account
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Accounts</h3>
          <div className="stat-value">{stats.total_accounts || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Active Accounts</h3>
          <div className="stat-value">{stats.active_accounts || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Platforms</h3>
          <div className="stat-value">{stats.platforms_with_accounts || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Active Sessions</h3>
          <div className="stat-value">{stats.active_sessions || 0}</div>
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
      {success && (
        <div className="alert alert-success">
          {success}
          <button onClick={() => setSuccess('')}>×</button>
        </div>
      )}

      {/* Accounts Grid */}
      <div className="accounts-grid">
        {accounts.map((account) => (
          <div 
            key={account.id} 
            className={`account-card ${selectedAccount?.id === account.id ? 'selected' : ''}`}
            onClick={() => setSelectedAccount(account)}
          >
            <div className="account-header">
              <div className="platform-info">
                <span className="platform-icon">{getPlatformIcon(account.platform)}</span>
                <span className="platform-name">{account.platform}</span>
              </div>
              <div 
                className="status-indicator"
                style={{ backgroundColor: getStatusColor(account.status) }}
                title={account.status}
              ></div>
            </div>
            
            <div className="account-details">
              <h4>{account.display_name || account.username}</h4>
              <p className="username">@{account.username}</p>
              {account.email && <p className="email">{account.email}</p>}
            </div>

            <div className="account-meta">
              <div className="meta-item">
                <span>Status:</span>
                <span className={`status ${account.status}`}>{account.status}</span>
              </div>
              <div className="meta-item">
                <span>Session:</span>
                <span className={account.session_valid ? 'valid' : 'expired'}>
                  {account.session_valid ? 'Valid' : 'Expired'}
                </span>
              </div>
              {account.last_activity && (
                <div className="meta-item">
                  <span>Last Activity:</span>
                  <span>{new Date(account.last_activity).toLocaleDateString()}</span>
                </div>
              )}
            </div>

            <div className="account-actions">
              <button 
                className="btn btn-sm btn-secondary"
                onClick={(e) => {
                  e.stopPropagation();
                  handleTestConnection(account.id);
                }}
                disabled={loading}
              >
                Test
              </button>
              {account.status === 'active' && (
                <button 
                  className="btn btn-sm btn-warning"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleLogout(account.id);
                  }}
                  disabled={loading}
                >
                  Logout
                </button>
              )}
              <button 
                className="btn btn-sm btn-info"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRefreshTokens(account.id);
                }}
                disabled={loading}
              >
                Refresh
              </button>
              <button 
                className="btn btn-sm btn-danger"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteAccount(account.id);
                }}
                disabled={loading}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Account Details Panel */}
      {selectedAccount && (
        <div className="account-details-panel">
          <h3>Account Details</h3>
          <div className="details-grid">
            <div className="detail-item">
              <label>Platform:</label>
              <span>{selectedAccount.platform}</span>
            </div>
            <div className="detail-item">
              <label>Username:</label>
              <span>{selectedAccount.username}</span>
            </div>
            <div className="detail-item">
              <label>Display Name:</label>
              <span>{selectedAccount.display_name}</span>
            </div>
            <div className="detail-item">
              <label>Email:</label>
              <span>{selectedAccount.email || 'Not provided'}</span>
            </div>
            <div className="detail-item">
              <label>Status:</label>
              <span className={`status ${selectedAccount.status}`}>
                {selectedAccount.status}
              </span>
            </div>
            <div className="detail-item">
              <label>Login Method:</label>
              <span>{selectedAccount.login_method}</span>
            </div>
            <div className="detail-item">
              <label>Capabilities:</label>
              <span>{selectedAccount.capabilities?.join(', ') || 'None'}</span>
            </div>
            <div className="detail-item">
              <label>Created:</label>
              <span>{new Date(selectedAccount.created_at).toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <label>Last Login:</label>
              <span>
                {selectedAccount.last_login 
                  ? new Date(selectedAccount.last_login).toLocaleString()
                  : 'Never'
                }
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Login Modal */}
      {showLoginModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Add Social Media Account</h3>
              <button 
                className="close-btn"
                onClick={() => setShowLoginModal(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              {/* Platform Selection */}
              <div className="form-group">
                <label>Platform:</label>
                <select 
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                >
                  <option value="">Select Platform</option>
                  {platforms.map((platform) => (
                    <option key={platform.name} value={platform.name}>
                      {platform.display_name}
                    </option>
                  ))}
                </select>
              </div>

              {selectedPlatform && (
                <>
                  {/* Login Method Selection */}
                  <div className="form-group">
                    <label>Login Method:</label>
                    <div className="radio-group">
                      <label>
                        <input 
                          type="radio"
                          value="oauth"
                          checked={loginMethod === 'oauth'}
                          onChange={(e) => setLoginMethod(e.target.value)}
                        />
                        OAuth (Recommended)
                      </label>
                      <label>
                        <input 
                          type="radio"
                          value="credentials"
                          checked={loginMethod === 'credentials'}
                          onChange={(e) => setLoginMethod(e.target.value)}
                        />
                        Username/Password
                      </label>
                    </div>
                  </div>

                  {loginMethod === 'oauth' ? (
                    <div className="oauth-section">
                      <p>Click the button below to authenticate with {selectedPlatform}:</p>
                      <button 
                        className="btn btn-primary btn-large"
                        onClick={() => handleOAuthLogin(selectedPlatform)}
                        disabled={loading}
                      >
                        {loading ? 'Connecting...' : `Connect to ${selectedPlatform}`}
                      </button>
                    </div>
                  ) : (
                    <div className="credentials-section">
                      <div className="form-group">
                        <label>Username/Email:</label>
                        <input 
                          type="text"
                          value={loginForm.username}
                          onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                          placeholder="Enter username or email"
                        />
                      </div>
                      <div className="form-group">
                        <label>Password:</label>
                        <input 
                          type="password"
                          value={loginForm.password}
                          onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                          placeholder="Enter password"
                        />
                      </div>
                      <div className="form-group">
                        <label>Email (optional):</label>
                        <input 
                          type="email"
                          value={loginForm.email}
                          onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                          placeholder="Enter email"
                        />
                      </div>
                      <div className="form-group">
                        <label>Display Name (optional):</label>
                        <input 
                          type="text"
                          value={loginForm.displayName}
                          onChange={(e) => setLoginForm({...loginForm, displayName: e.target.value})}
                          placeholder="Enter display name"
                        />
                      </div>
                      <button 
                        className="btn btn-primary btn-large"
                        onClick={handleCredentialLogin}
                        disabled={loading || !loginForm.username || !loginForm.password}
                      >
                        {loading ? 'Logging in...' : 'Login'}
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
};

export default SocialAccountManager;

