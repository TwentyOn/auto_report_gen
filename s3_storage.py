from datetime import timedelta
from io import BytesIO
import logging

from settings import (
    ACCESS_KEY,
    BUCKET_NAME,
    ENDPOINT_URL,
    SECURE,
    OUTER_ENDPOINT_URL,
    SECRET_KEY,
)
from minio import Minio

logger = logging.getLogger(__file__)


class MyStorage:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str, secure: bool = False):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,  # отключение подключения по HTTPS
        )
        self.bucket_name = bucket_name
        print("Подключение к хранилищу успешно")

    def upload_file(self, file_name: str, file_path: str):
        """
        Загрузка файла в S3-хранилище
        :param file_name: путь для сохранения файла в хранилище
        :param file_path: путь к файлу в файловой системе
        :return: None
        """
        self.client.fput_object(self.bucket_name, file_name, file_path)

    def upload_memory_file(self, file_name: str, data: BytesIO, length: int):
        """
        Загрузка файла из оперативной памяти
        :param file_name: путь для сохранения файла в хранилище
        :param data: файл (бинарный)
        :param length:
        :return:
        """
        self.client.put_object(self.bucket_name, file_name, data, length)

    def download_file(self, obj_name) -> tuple | bool:
        response = self.client.get_object(self.bucket_name, obj_name)
        data, status = response.read().decode('utf-8'), response.status
        response.release_conn()
        response.close()
        return data, status

    def get_list_objects(self, path: str = None):
        if path:
            return self.client.list_objects(self.bucket_name, prefix=path)
        return self.client.list_objects(self.bucket_name)

    def share_file_from_bucket(self, file_name, expire=timedelta(seconds=60)):
        """
        Генерирует ссылку на скачивание файла
        :param backet_name:
        :param file_name:
        :param expire:
        :return:
        """
        # return self.client.presigned_get_object(bucket_name, file_name, expire)
        return f"http{'s' if SECURE else ''}://{OUTER_ENDPOINT_URL}/minio/{self.bucket_name}/{file_name}"


storage = MyStorage(ENDPOINT_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME)
