def parse_payload(data):
    """
    Parses a Stripe charge.succeeded event webhook payload.
    """
    amount = data.get('data', {}).get('object', {}).get('amount')
    currency = data.get('data', {}).get('object', {}).get('currency')
    customer_email = data.get('data', {}).get('object', {}).get('billing_details', {}).get('email')

    return {
        'amount': amount / 100 if amount is not None else None,
        'currency': currency,
        'customer_email': customer_email,
    }