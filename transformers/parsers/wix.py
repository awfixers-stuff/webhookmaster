def parse_payload(data):
    """
    Parses a Wix webhook payload (order-related example).
    """
    order_number = data.get('orderNumber')
    total_price = None
    currency = None

    payments = data.get('payments')
    if payments and isinstance(payments, list) and len(payments) > 0:
        payment = payments[0]
        amount_data = payment.get('amount', {})
        total_price = amount_data.get('value')
        currency = amount_data.get('currency')
    else:
        line_items = data.get('lineItems')
        if line_items and isinstance(line_items, list) and len(line_items) > 0:
            line_item = line_items[0]
            total_price_data = line_item.get('totalPrice', {})
            total_price = total_price_data.get('value')
            currency = total_price_data.get('currency')

    return {
        'order_number': order_number,
        'total_price': total_price,
        'currency': currency,
    }