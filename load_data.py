import io
import os

from docx_report_generator.s3_storage import storage

FILES_PATH = 'docx_report_generator/example/input_data'

for file in os.scandir(FILES_PATH):
    filename = file.name

    with open(file, encoding='utf-8') as f:
        file = io.BytesIO(f.read().encode())
    file.seek(0)

    storage.upload_memory_file(f'products_report_generator/1/csv_exports/{filename}', file, len(file.getvalue()))