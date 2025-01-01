import os
from dotenv import load_dotenv

load_dotenv(".env")
REDIS_URL = os.environ.get('REDIS_URL')

# Redis connection URLs
broker_url = f"{REDIS_URL}"  
result_backend = f"{REDIS_URL}" 
