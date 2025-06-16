import os
import redis
from rq import Worker, Queue
from urllib.parse import urlparse

redis_url_str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Parse the URL to extract host, port, and db
url = urlparse(redis_url_str)
redis_host = url.hostname
redis_port = url.port
redis_db = int(url.path.replace('/', '')) if url.path else 0

redis_conn = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
# Define which queues this worker should process
listen = ['rooftop_detection']

if __name__ == '__main__':
    # Create required directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Start the worker
    queues = [Queue(name, connection=redis_conn) for name in listen]
    worker = Worker(queues, connection=redis_conn)
    print(f"Worker started, listening to queues: {listen}")
    worker.work()
