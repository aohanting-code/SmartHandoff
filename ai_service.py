
import re


def analyse(message, previous='other'):
    text = message.lower().strip()

    patterns = {
        'refund': (
            r'\b(refund|money back|payment|reimbursement)\b'
        ),
        'return': (
            r'\b(return|send back)\b'
        ),
        'delivery': (
            r'\b(delivery|parcel|tracking|shipping|'
            r'order status|order|package|shipment|arrived)\b'
        )
    }

    intent = next(
        (key for key, pattern in patterns.items()
         if re.search(pattern, text)),
        None
    )

    # Use the previous intent for recognised follow-up phrases.
    follow_up = (
        r'\b(still|again|already|wait|waiting|'
        r'not helped|not working|where is it|'
        r'find it|check it|track it|help me|'
        r'any update|what about it)\b'
    )

    if not intent:
        if previous != 'other' and re.search(follow_up, text):
            intent = previous
        else:
            intent = 'other'

    negative = bool(re.search(
        r'frustrat|angry|annoy|ridiculous|'
        r'unacceptable|not helped|upset|disappointed',
        text
    ))

    manual = bool(re.search(
        r'\b(human|real person|human agent)\b',
        text
    ))

    return {
        'intent': intent,
        'negative': negative,
        'manual': manual
    }
