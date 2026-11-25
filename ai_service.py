import re

def analyse(message, previous='other'):
    text = message.lower()
    patterns = {'refund': r'refund|money back|payment', 'delivery': r'delivery|parcel|tracking|shipping|order status', 'return': r'return|send back'}
    intent = next((k for k,v in patterns.items() if re.search(v,text)), None)
    if not intent:
        intent = previous if re.search(r'still|again|already|wait|not helped|not working|where is it',text) else 'other'
    return {'intent':intent, 'negative':bool(re.search(r'frustrat|angry|annoy|ridiculous|unacceptable|not helped',text)), 'manual':bool(re.search(r'\b(human|real person|human agent)\b',text))}
