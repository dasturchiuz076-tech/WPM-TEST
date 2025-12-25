def user_profile_processor(request):
    """Attach the user's profile to the template context if available."""
    user_profile = None
    try:
        if request.user.is_authenticated:
            user_profile = getattr(request.user, 'profile', None)
    except Exception:
        user_profile = None

    return {
        'user_profile': user_profile
    }