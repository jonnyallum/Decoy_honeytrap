# Social Media Account Management Integration

## Overview

The AI Honeytrap Network now includes comprehensive social media account management functionality that allows operators to log into and manage multiple social media accounts directly from the application. This feature enables seamless switching between different platforms and accounts while maintaining secure session management.

## Features

### 🔐 **Multi-Platform Authentication**
- **OAuth Integration**: Secure OAuth 2.0 authentication for supported platforms
- **Credential-Based Login**: Username/password authentication for platforms without OAuth
- **Browser Automation**: Automated login for complex authentication flows
- **Session Persistence**: Secure storage and restoration of authentication sessions

### 📱 **Supported Platforms**
- **Facebook**: OAuth and credential-based authentication
- **Instagram**: OAuth and browser automation
- **Twitter/X**: OAuth integration
- **Discord**: OAuth and bot token authentication
- **TikTok**: Browser automation and API integration
- **Snapchat**: Browser automation
- **LinkedIn**: OAuth integration
- **YouTube**: OAuth integration

### 🔄 **Session Management**
- **Multiple Active Sessions**: Manage multiple accounts simultaneously
- **Session Switching**: Seamlessly switch between different accounts
- **Session Persistence**: Sessions survive application restarts
- **Automatic Cleanup**: Expired sessions are automatically cleaned up
- **Rate Limiting**: Built-in rate limiting per platform and action

### 🛡️ **Security Features**
- **Encrypted Storage**: All credentials and tokens are encrypted at rest
- **Secure Transmission**: All communications use TLS encryption
- **Access Controls**: Role-based access to account management features
- **Audit Logging**: Complete audit trail of all account activities
- **Token Refresh**: Automatic token refresh for OAuth sessions

## Architecture

### Backend Components

#### 1. Social Account Model (`models/social_account.py`)
```python
class SocialAccount:
    - id: Unique account identifier
    - platform: Social media platform name
    - username: Account username
    - display_name: Account display name
    - email: Associated email address
    - status: Account status (active, inactive, error, suspended)
    - login_method: Authentication method (oauth, credentials, browser)
    - capabilities: List of supported actions
    - created_at: Account creation timestamp
    - last_login: Last successful login timestamp
```

#### 2. Authentication Manager (`services/social_auth_manager.py`)
- OAuth flow management
- Credential validation
- Token refresh handling
- Platform-specific authentication logic

#### 3. Session Manager (`services/session_manager.py`)
- Multi-session management
- Session switching logic
- Rate limiting enforcement
- Activity logging

#### 4. Browser Automation (`services/browser_automation.py`)
- Selenium-based automation
- Platform-specific login flows
- Session restoration
- Captcha handling

#### 5. Platform Integrations (`services/platform_integrations.py`)
- Platform-specific API clients
- OAuth configuration
- Rate limit definitions
- Capability mappings

### Frontend Components

#### 1. Social Account Manager (`components/admin/SocialAccountManager.jsx`)
- Account listing and management
- Login modal with OAuth and credential options
- Session switching interface
- Account statistics dashboard

#### 2. Account Management CSS (`components/admin/SocialAccountManager.css`)
- Professional styling for account management interface
- Responsive design for mobile and desktop
- Visual indicators for account status and session state

## API Endpoints

### Account Management

#### `POST /api/accounts`
Create a new social media account
```json
{
  "platform": "facebook",
  "login_method": "oauth",
  "username": "user@example.com",
  "display_name": "John Doe"
}
```

#### `GET /api/accounts`
List all social media accounts
```json
{
  "accounts": [
    {
      "id": "account_123",
      "platform": "facebook",
      "username": "user@example.com",
      "status": "active",
      "last_login": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `PUT /api/accounts/{account_id}`
Update account information
```json
{
  "display_name": "Updated Name",
  "status": "active"
}
```

#### `DELETE /api/accounts/{account_id}`
Delete an account

### Authentication

#### `GET /api/auth/platforms`
Get list of supported platforms
```json
{
  "platforms": [
    {
      "name": "facebook",
      "display_name": "Facebook",
      "oauth_supported": true,
      "credentials_supported": true,
      "browser_supported": true
    }
  ]
}
```

#### `GET /api/auth/oauth/{platform}`
Start OAuth authentication flow
```json
{
  "auth_url": "https://facebook.com/oauth/authorize?...",
  "state": "random_state_string"
}
```

#### `POST /api/auth/credentials`
Authenticate with username/password
```json
{
  "platform": "facebook",
  "username": "user@example.com",
  "password": "secure_password"
}
```

### Session Management

#### `POST /api/sessions`
Create a new session
```json
{
  "account_id": "account_123",
  "session_type": "api"
}
```

#### `GET /api/sessions`
Get user's active sessions
```json
{
  "sessions": [
    {
      "session_id": "session_456",
      "account_id": "account_123",
      "platform": "facebook",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `POST /api/sessions/{session_id}/switch`
Switch to a different session

#### `POST /api/sessions/{session_id}/action`
Perform an action using a session
```json
{
  "action": "post",
  "parameters": {
    "content": "Hello, world!",
    "visibility": "public"
  }
}
```

#### `DELETE /api/sessions/{session_id}`
Close a session

## Usage Guide

### Adding a New Account

1. **Navigate to Social Accounts Tab**
   - Open the Admin Dashboard
   - Click on the "Social Accounts" tab

2. **Click "Add Account"**
   - Select the desired platform
   - Choose authentication method (OAuth recommended)

3. **Complete Authentication**
   - For OAuth: Complete the authorization flow in the popup window
   - For Credentials: Enter username and password

4. **Verify Account**
   - Account will appear in the accounts list
   - Status should show as "active"

### Managing Sessions

1. **Create Session**
   - Click on an account card
   - Session will be automatically created
   - Account card will show "active" session indicator

2. **Switch Between Accounts**
   - Click on different account cards to switch sessions
   - Current session is highlighted
   - Session switching is instantaneous

3. **Perform Actions**
   - Use the chat interfaces or content management tools
   - Actions will be performed using the currently active session
   - Rate limits are enforced per account

### Monitoring and Maintenance

1. **Account Status Monitoring**
   - Green indicator: Account is active and session is valid
   - Yellow indicator: Account is active but session expired
   - Red indicator: Account has errors or is suspended
   - Gray indicator: Account is inactive

2. **Session Management**
   - Sessions automatically expire after 1 hour of inactivity
   - Use "Extend" button to extend session timeout
   - Use "Refresh" button to refresh OAuth tokens
   - Use "Test" button to verify account connectivity

3. **Troubleshooting**
   - Check account status indicators
   - Review activity logs in account details
   - Use test connection feature to diagnose issues
   - Refresh tokens if authentication fails

## Security Considerations

### Data Protection
- All credentials are encrypted using AES-256 encryption
- OAuth tokens are stored securely and refreshed automatically
- Session data is encrypted both at rest and in transit
- Sensitive information is never logged in plain text

### Access Controls
- Account management requires admin privileges
- Users can only access their own sessions
- Role-based permissions for different operations
- Audit logging for all account activities

### Rate Limiting
- Platform-specific rate limits are enforced
- Rate limit status is displayed in the interface
- Automatic backoff when limits are approached
- Rate limit reset times are tracked and displayed

### Session Security
- Sessions have configurable timeout periods
- Automatic cleanup of expired sessions
- Secure session token generation
- Protection against session hijacking

## Configuration

### Environment Variables
```bash
# OAuth Configuration
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret

# Encryption
ENCRYPTION_KEY=your_32_byte_encryption_key

# Session Configuration
SESSION_TIMEOUT=3600  # 1 hour in seconds
MAX_SESSIONS_PER_USER=10
```

### Platform Configuration
Each platform can be configured with specific settings:
```json
{
  "facebook": {
    "oauth_enabled": true,
    "credentials_enabled": true,
    "browser_enabled": true,
    "rate_limits": {
      "posts_per_hour": 25,
      "messages_per_hour": 100
    },
    "capabilities": ["post", "message", "read_profile"]
  }
}
```

## Troubleshooting

### Common Issues

#### OAuth Authentication Fails
- Verify client ID and secret are correct
- Check redirect URI configuration
- Ensure platform app is approved for production use

#### Session Creation Fails
- Check account status is "active"
- Verify credentials are still valid
- Check platform API status

#### Rate Limits Exceeded
- Wait for rate limit reset time
- Reduce action frequency
- Use multiple accounts to distribute load

#### Browser Automation Issues
- Check if platform has changed login flow
- Update browser automation scripts
- Verify browser dependencies are installed

### Debugging

#### Enable Debug Logging
```python
import logging
logging.getLogger('social_auth_manager').setLevel(logging.DEBUG)
logging.getLogger('session_manager').setLevel(logging.DEBUG)
```

#### Check Session Status
```bash
curl -X GET http://localhost:5000/api/sessions/stats
```

#### Test Account Connectivity
```bash
curl -X POST http://localhost:5000/api/accounts/{account_id}/test
```

## Best Practices

### Account Management
- Use OAuth authentication when available
- Regularly test account connectivity
- Monitor rate limit usage
- Keep credentials secure and rotate regularly

### Session Management
- Close unused sessions to free resources
- Monitor session activity logs
- Use appropriate session types for different use cases
- Implement proper error handling

### Security
- Use strong encryption keys
- Implement proper access controls
- Monitor audit logs regularly
- Follow platform security guidelines

### Performance
- Limit concurrent sessions per user
- Implement connection pooling for API clients
- Cache frequently accessed data
- Monitor resource usage

## Future Enhancements

### Planned Features
- **Multi-Factor Authentication**: Support for 2FA/MFA
- **Advanced Rate Limiting**: Dynamic rate limit adjustment
- **Session Analytics**: Detailed session usage analytics
- **Bulk Operations**: Batch account management operations
- **Mobile App Integration**: Native mobile app support

### Platform Expansion
- **Telegram**: Bot and user account integration
- **WhatsApp Business**: Business API integration
- **Reddit**: OAuth and bot account support
- **Pinterest**: OAuth and API integration

### Advanced Features
- **Account Clustering**: Group related accounts
- **Automated Failover**: Automatic account switching on errors
- **Load Balancing**: Distribute actions across multiple accounts
- **Advanced Analytics**: Cross-platform analytics and reporting

