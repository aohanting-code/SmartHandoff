def decide(count, negative=False, unsupported=False, resolved=False, declined=False):
    if resolved or declined:
        return None
    if unsupported:
        return 'The available records cannot resolve this request.'
    if count >= 3:
        return 'The same issue has been raised repeatedly without confirmation of resolution.'
    if count >= 2 and negative:
        return 'The issue remains open and your message suggests frustration.'
    return None
