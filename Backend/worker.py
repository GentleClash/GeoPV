import os
import redis
from rq import Worker, Queue

# Configure Redis connection
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

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