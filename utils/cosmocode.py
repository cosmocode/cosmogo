def is_from_cosmocode(user):
    if user.is_anonymous or not user.is_superuser:
        return False

    email = user.email

    if not email:
        return False

    try:
        _, domain = email.rsplit('@', 1)
    except ValueError:
        return False

    return domain == 'cosmocode.de'
