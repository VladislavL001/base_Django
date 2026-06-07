def roles(request):
    user = getattr(request, 'user', None)
    is_manager = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name='Managers').exists())
    )
    return {'is_manager': is_manager}
