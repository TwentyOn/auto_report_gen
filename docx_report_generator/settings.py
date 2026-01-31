import os

import dotenv

dotenv.load_dotenv()

# БД
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_SCHEME = 'campaign_stats'

# Minio
ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
OUTER_ENDPOINT_URL = os.getenv('S3_OUTER_ENDPOINT_URL')
ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
SECRET_KEY = os.getenv('S3_SECRET_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
SECURE = os.getenv('S3_SECURE')
