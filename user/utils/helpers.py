

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


def get_reset_email_content(username: str,
                        url: str) -> str:
    """
    Return the content for forgotten password reset emails.
    """

    return f"""
    Hi, {username},
    
    You've requested to reset your password. Please click the link below to set a new password:
     
    {url}
     
    This link is valid for an hour. If you didn't request this password reset, please ignore this email.
            
    Thank you,
    Team Interpredators
    """