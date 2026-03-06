import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

def get_cache(key: str):
    """
    Get data from the Redis cache.
    Returns parsed Json if found, none if not found.
    """
    try:
        data = r.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None

def set_cache(key: str, value, expiry_seconds: int = 3600):
    """
    Store data in Redis cache.
    Default expiry is 1 hour (3600 seconds).
    """
    try:
        r.set(key, json.dumps(value), ex=expiry_seconds)
    except Exception as e:
        print(f"Cache set error: {e}")


def delete_cache(key: str):
    """
    Delete a specific key from Redis cache.
    """
    try:
        r.delete(key)
    except Exception as e:
        print(f"Cache delete error: {e}")