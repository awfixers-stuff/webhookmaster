def parse_payload(data):
    """
    Parses a Cloudflare webhook payload.
    """
    parsed_data = {
        'name': data.get('name'),
        'text': data.get('text'),
        'timestamp': data.get('ts'),
    }

    # Extract specific data based on event type if available
    if 'data' in data and isinstance(data['data'], dict):
        if data['data'].get('event_type') == 'live_input.disconnected':
            parsed_data['event_type'] = data['data']['event_type']
            parsed_data['input_id'] = data['data']['input_id']
        elif data['data'].get('alert_name') == 'pages_event_alert':
            parsed_data['event'] = data['data']['event']
            parsed_data['project_name'] = data['data']['project_name']
            parsed_data['commit_hash'] = data['data']['commit_hash']

    return parsed_data