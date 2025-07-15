def format_payload(data):
    """
    Formats the payload for Slack.
    """
    return {'text': f"New webhook received: {data.get('message')}"}