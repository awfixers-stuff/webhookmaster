def format_payload(data):
    """
    Formats the payload for email.
    """
    subject = data.get('subject', 'Webhook Notification')
    body = data.get('body', str(data))
    return {'subject': subject, 'body': body}