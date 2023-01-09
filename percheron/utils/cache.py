
from requests_cache import CachedSession

def session(): 
    # Note: POST may be ignored by default! So ensure we cache that. 
    return CachedSession('api_cache', backend='sqlite', allowable_methods=('GET', 'POST'))