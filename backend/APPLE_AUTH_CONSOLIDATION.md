# Apple Sign-In Authentication Consolidation

## Overview

This document describes the consolidation of Apple Sign-In authentication across three applications:

- **PoppyTracker** - Pet feeding tracker
- **SpeechCoach** - Speech analysis and coaching
- **SideQuest** - Daily quest generation

## What Was Consolidated

### Before (Code Duplication)

- **Legacy Implementation** (`backend/src/auth.py`): Used by PoppyTracker and SpeechCoach

  - Used `requests` library
  - Basic token validation
  - Simple user creation/update
  - No admin role handling

- **New Implementation** (`backend/src/apple_auth_service.py`): Used by SideQuest
  - Used `httpx` library
  - Enhanced token validation
  - Comprehensive user field updates
  - Admin role assignment

### After (Consolidated)

- **Single Service** (`backend/src/apple_auth_service.py`): Used by all three apps
  - Uses `httpx` for better performance
  - Enhanced token validation with development mode support
  - Comprehensive user field updates for all apps
  - Admin role assignment for all apps
  - Backward compatibility maintained

## Key Features

### 1. Enhanced Token Validation

- **Production Mode**: Strict audience verification with bundle ID
- **Development Mode**: Bypasses audience verification for testing convenience
- **Fallback Mode**: Uses token's own audience when no client_id provided

### 2. Admin Role Assignment

All apps now support admin role assignment based on `ADMIN_EMAILS` configuration:

```python
# In your Flask config
ADMIN_EMAILS = ["admin@example.com", "superuser@example.com"]
```

### 3. Comprehensive User Updates

- Name updates from Apple's fullName components
- Email updates when provided
- Apple ID updates
- Default avatar assignment
- Enhanced logging with app identification

### 4. Public Key Caching

- 24-hour cache for Apple's public keys
- Automatic refresh when expired
- Better performance and reduced API calls

## Usage

### For New Apps

```python
from backend.src.apple_auth_service import get_apple_auth_service

# Get the service
auth_service = get_apple_auth_service()

# Authenticate user
user = auth_service.authenticate_with_apple(
    apple_credential,
    client_id="com.yourapp.bundleid",  # Optional
    app_name="YourAppName"
)
```

### For Existing Apps (Backward Compatible)

```python
from backend.src.apple_auth_service import apple_signin

# Legacy function still works
user = apple_signin(apple_credential)
```

### App-Specific Routes

Each app now uses the consolidated service with proper identification:

#### PoppyTracker

```python
user = get_apple_auth_service().authenticate_with_apple(
    credentials,
    app_name="PoppyTracker"
)
```

#### SpeechCoach

```python
user = get_apple_auth_service().authenticate_with_apple(
    credentials,
    app_name="SpeechCoach"
)
```

#### SideQuest

```python
user = get_apple_auth_service().authenticate_with_apple(
    credentials,
    client_id="com.lkleinbrodt.SideQuest",
    app_name="SideQuest"
)
```

## Development Mode Behavior

**⚠️ IMPORTANT SECURITY NOTE**: In development mode (`current_app.debug=True`), audience verification is bypassed for convenience. This is **NOT secure** for production use.

```python
# Development mode warning log:
"DEVELOPMENT MODE: Bypassing Apple token audience verification. This is NOT secure for production use!"
```

### When Audience Verification is Bypassed

- `current_app.debug = True` (development mode)
- No `client_id` provided
- Token's own audience is logged for debugging

### When Audience Verification is Enforced

- `current_app.debug = False` (production mode)
- `client_id` is provided
- Strict validation against the provided bundle ID

## Configuration

### Required Environment Variables

```bash
# Apple Sign-In configuration
ADMIN_EMAILS=["admin@example.com", "superuser@example.com"]

# App-specific bundle IDs (optional, for production)
SIDEQUEST_BUNDLE_ID="com.lkleinbrodt.SideQuest"
POPPYTRACKER_BUNDLE_ID="com.lkleinbrodt.poppytracker"
SPEECHCOACH_BUNDLE_ID="com.lkleinbrodt.speechcoach"
```

### Optional Configuration

- **Bundle IDs**: For production audience verification
- **Admin Emails**: For role assignment
- **Development Mode**: Automatically detected from Flask config

## Testing

Comprehensive tests are available in `tests/test_apple_auth_consolidation.py`:

```bash
# Run all Apple Auth tests
pytest tests/test_apple_auth_consolidation.py -v

# Run specific test categories
pytest tests/test_apple_auth_consolidation.py::TestAppleAuthService -v
pytest tests/test_apple_auth_consolidation.py::TestBackwardCompatibility -v
pytest tests/test_apple_auth_consolidation.py::TestTokenValidation -v
```

## Migration Guide

### For Existing Apps

1. **No Code Changes Required**: Legacy functions still work
2. **Enhanced Functionality**: Automatically get admin roles and better user updates
3. **Better Logging**: App-specific logging for debugging

### For New Apps

1. **Use the Service**: `get_apple_auth_service().authenticate_with_apple()`
2. **Provide App Name**: For logging and identification
3. **Optional Bundle ID**: For production security

## Security Considerations

### Production Requirements

- **Always** provide `client_id` (bundle ID) in production
- **Never** use development mode in production
- **Verify** `ADMIN_EMAILS` configuration is secure

### Development Convenience

- Audience verification bypassed for testing
- Clear warnings in logs
- Automatic detection of development mode

## Performance Improvements

### Before

- Multiple HTTP requests for Apple public keys
- No caching
- Different HTTP libraries per app

### After

- Single HTTP request with 24-hour caching
- Consistent `httpx` usage
- Optimized key lookup

## Error Handling

### Enhanced Error Messages

- App-specific logging with `[AppName]` prefix
- Detailed error context
- Graceful fallbacks for missing data

### Common Error Scenarios

- Missing identity token
- Invalid token format
- Expired tokens
- Network failures
- Invalid audience (production only)

## Future Enhancements

### Potential Improvements

1. **Rate Limiting**: For Apple public key requests
2. **Metrics**: Authentication success/failure tracking
3. **Audit Logging**: User creation and role changes
4. **Multi-Provider**: Support for Google, Facebook, etc.

### Configuration Options

1. **Custom Cache Duration**: Configurable public key cache TTL
2. **Retry Logic**: Automatic retry for failed key fetches
3. **Health Checks**: Service availability monitoring

## Support

For questions or issues with the consolidated Apple Auth service:

1. **Check Logs**: App-specific logging with `[AppName]` prefix
2. **Run Tests**: Ensure all tests pass
3. **Review Configuration**: Verify environment variables
4. **Check Development Mode**: Ensure proper audience verification

## Changelog

### v2.0.0 (Consolidation)

- ✅ Consolidated all Apple Sign-In implementations
- ✅ Enhanced token validation with development mode support
- ✅ Admin role assignment for all apps
- ✅ Comprehensive user field updates
- ✅ Public key caching with httpx
- ✅ Backward compatibility maintained
- ✅ App-specific logging and identification
- ✅ Comprehensive test coverage

### v1.x (Legacy)

- Basic token validation
- Simple user management
- App-specific implementations
- Limited error handling
