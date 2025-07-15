def parse_payload(data):
    """
    Parses a Webflow form submission webhook payload.
    """
    form_data = data.get('data', {})
    return {
        'form_id': data.get('formId'),
        'submission_id': data.get('submissionId'),
        'triggered_by': data.get('triggeredBy'),
        'email': form_data.get('email'),
        'name': form_data.get('name'),
        'all_fields': form_data # Include all form fields for flexibility
    }