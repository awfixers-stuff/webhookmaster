def parse_payload(data):
    """
    Parses a GitHub push event webhook payload.
    """
    repository_full_name = data.get('repository', {}).get('full_name')
    pusher_name = data.get('pusher', {}).get('name')
    commits_count = len(data.get('commits', []))

    return {
        'repository': repository_full_name,
        'pusher': pusher_name,
        'commits': commits_count,
    }