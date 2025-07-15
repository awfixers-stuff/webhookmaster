def parse_payload(data):
    """
    Parses a Shopify orders/create webhook payload.
    """
    return {
        'order_id': data.get('id'),
        'total_price': data.get('total_price'),
        'currency': data.get('currency'),
        'customer_email': data.get('email'),
    }