def format_payload(data):
    """
    Formats the payload for Microsoft Teams.
    """
    amount = data.get('amount', 'N/A')
    currency = data.get('currency', 'N/A').upper()
    customer_email = data.get('customer_email', 'N/A')

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "New charge succeeded",
        "sections": [{
            "activityTitle": "New charge succeeded",
            "facts": [{
                "name": "Amount",
                "value": f"{amount} {currency}"
            }, {
                "name": "Customer Email",
                "value": customer_email
            }]
        }]
    }