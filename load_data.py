import io
import os

from minio import Minio
import dotenv

dotenv.load_dotenv()

FILES_PATH = 'docx_report_generator/example/input_data'  # путь к csv-файлам
S3_PATH = 'products_report_generator/{{REPORT_ID}}/csv_exports/{{FILENAME}}'  # шаблон пути для сохранения в S3


def upload_test_data():
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    client = Minio(endpoint='127.0.0.1:9000', access_key=access_key, secret_key=secret_key, secure=False)
    for file in os.scandir(FILES_PATH):
        filename = file.name

        with open(file, encoding='utf-8') as f:
            file = io.BytesIO(f.read().encode())
        file.seek(0)
        save_path = S3_PATH.replace('{{REPORT_ID}}', '1').replace('{{FILENAME}}', filename)
        client.put_object(bucket_name, save_path, file, len(file.getvalue()))


if __name__ == '__main__':
    upload_test_data()
