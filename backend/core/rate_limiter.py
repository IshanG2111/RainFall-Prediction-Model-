from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance for entire app
limiter = Limiter(key_func=get_remote_address)