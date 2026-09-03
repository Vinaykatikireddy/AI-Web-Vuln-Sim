from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiting (keyed by client IP)
limiter = Limiter(key_func=get_remote_address)
