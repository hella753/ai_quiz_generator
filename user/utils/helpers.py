

def get_verification_email_content(username: str,
                                   verification_url: str) -> str:
    """
    Return the content for verification emails.
    """
    return f"""
    Hi, {username},

    Please verify your account by clicking on the link below:
    {verification_url}

    This link will expire in 48 hours.

    Regards,
    Team Interpredators
    """
