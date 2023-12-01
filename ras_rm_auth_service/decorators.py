from functools import wraps
import logging
import time

import structlog

logger = structlog.wrap_logger(logging.getLogger(__name__))

def retry(exception_to_check, tries=4, delay=3, backoff=2):
    def decorator(f):
        @wraps(f)
        def retry_func(*args, **kwargs):
            current_tries, current_delay = tries, delay
            while current_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    logger.info(f"Retrying in {current_delay} seconds")
                    time.sleep(current_delay)
                    current_tries -= 1
                    current_delay *= backoff
            return f(*args, **kwargs)
        
        return retry_func
    
    return decorator
