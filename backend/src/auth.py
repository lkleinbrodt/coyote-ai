from backend.src.apple_auth_service import get_apple_auth_service


def apple_signin(apple_credential):
    """
    Handle apple signin, agnostic to app. Will simply output a User object
    whatever function is using this function can then add their user info as desired

    UPDATED: Now uses the consolidated Apple Auth Service for enhanced functionality.
    """
    # Use the consolidated service for better functionality
    return get_apple_auth_service().apple_signin(apple_credential, "legacy")
