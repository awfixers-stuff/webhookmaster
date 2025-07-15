def format_payload(data):
    """
    Formats the payload for Discord.
    """
    repository = data.get('repository', 'unknown repository')
    pusher = data.get('pusher', 'unknown user')
    commits = data.get('commits', 'unknown number of')

    return {
        'content': f"New push to {repository} by {pusher} with {commits} commits."
    }