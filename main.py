import logging
from typing import Sequence
import time
import io

from sqlalchemy import select, update, and_, Row
from sqlalchemy.orm import Session

from database.db import session_maker
from database.models import Report, Product
from s3_storage import storage
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format='[{asctime}] #{levelname:4} {name}:{lineno} - {message}', style='{')
logger = logging.getLogger(__file__)


class Processor:
    def __init__(self, session: Session):
        self.session: Session = session
        self.csv_path_template = 'products_report_generator/{{REPORT_ID}}/csv_exports/'
        self.docx_report_path_template = 'products_report_generator/{{REPORT_ID}}/docx_report/'
        self.target_files = {'текущая рк.csv': 'cur_rk', 'органический трафик.csv': 'org',
                             'группы по типу рк.csv': 'groups',
                             'все кампании.csv': 'campaigns', 'предыдущая рк.csv': 'prev_rk'}

    def get_reports(self, target_status_id: int) -> Sequence[Row[tuple]]:
        """
        Метод получает идентификаторы запросов для формирования отчетов из БД
        :return: список идентификаторов
        """
        logger.info('Поиск запросов для подготовки отчетов...')
        stmt = (
            select(Report.id, Product.name).
            join(Product, Report.product_id == Product.id).
            where(and_(Report.status_id == target_status_id, Report.to_delete == False))
        )

        reports_to_process = self.session.execute(stmt).all()
        logger.info(f'Найдено {len(reports_to_process)} запросов, готовых к обработке')
        return reports_to_process

    def process_report(self, report_id: int, header: str, outlier_rate: float = 1.5):
        logger.info(f'Обработка отчета [{report_id}]...')
        data = self.get_data_content(report_id)
        if not data:
            raise IOError('Нет данных для создания отчета')
        data['header'] = header
        data['outlier_rate'] = outlier_rate

        logger.info(f'Формирование файла...')
        new_report = ReportGenerator(**data)
        new_report.write_general_params()
        new_report.write_page_views()
        new_report.write_funnel_graph_section()
        new_report.write_outliers_section()
        new_report.write_groups_section()
        file = new_report.save_report(f'Отчет_{header.replace(" ", "_")}_{report_id}.docx', binary=True)
        logger.info('Файл сформирован')
        logger.info('Отправка файла в хранилище...')
        s3_filepath = self.upload_to_s3(file, file.name, report_id)
        return s3_filepath

    def get_data_content(self, report_id: int) -> dict | None:
        """
        Загрузка данных из S3-хранилища
        :param report_id:
        :return: словарь - имя параметра: csv-данные
        """
        path = self.csv_path_template.replace('{{REPORT_ID}}', str(report_id))
        logger.info(f'Скачивание данных из {path}...')

        result = {}
        obj_names = [obj.object_name for obj in storage.get_list_objects(path)]
        if not obj_names:
            logger.warning('Нет данных для создания отчета')
            return None

        # поиск и загрузка необходимых файлов бех учета регистра
        for obj_name in obj_names:
            filename = obj_name.split('/')[-1].lower()
            if filename in self.target_files:
                key = self.target_files[filename]
                content = self.download_data(obj_name)
                result[key] = content
        logger.info('Данные успешно загружены')
        return result

    @staticmethod
    def download_data(obj_name):
        """
        Метод для скачивание csv-контента из хранилища
        :param obj_name:
        :return:
        """
        logger.info(f'Скачивание файла {obj_name}...')
        for retry in range(3):
            try:
                content, status = storage.download_file(obj_name)
                if status != 200:
                    raise IOError(f'Ошибка скачивания файла: {content}')
                logger.info('Успех')
                return content
            except Exception as err:
                logger.warning(f'Ошибка при скачивании {obj_name}: {str(err)}')
                if retry == 2:
                    raise err
                logger.info(f'Попытка скачивания {retry + 1}...')

    def upload_to_s3(self, file: io.BytesIO, file_name: str, report_id: int):
        """
        Отправляет файл в S3-хранилище
        :param minio_client:
        :param file:
        :param file_name: имя файла - критически важно чтобы содержало ID отчёта для которого файл создан (19/filename.docx)
        :return:
        """
        error = None
        for _ in range(3):
            try:
                s3_report_path = self.docx_report_path_template.replace('{{REPORT_ID}}', str(report_id))
                output_path = ''.join((s3_report_path, file_name))
                storage.upload_memory_file(output_path, file, len(file.getvalue()))
                print(f'Файл отправлен в хранилище: {output_path}')
                return output_path
            except Exception as e:
                print(f'Ошибка отправки отчёта (попытка {_ + 1}) {file_name} в хранилище: {e}')
                error = e
                file.seek(0)
                continue
        print('Критическая ошибка отправки отчёта')
        raise error


def main_cycle(target_status_id: int, success_status_id: int):
    """
    Бесконечный цикл ожидающий новых запросов на обработку
    :param target_status_id: целевой статус для взятия запроса в обработку
    :param succses_status_id: статус, устанавливаемый для запросов в случае успешной обработки
    :return:
    """
    while True:
        corrupted_count = 0
        errors = {}
        with session_maker() as session:
            processor = Processor(session)
            reports = processor.get_reports(target_status_id)

            for report in reports:
                try:
                    report_id, header = report[0], report[1]
                    s3_filepath = processor.process_report(report_id, header)

                    session.execute(update(Report).
                                    values(content_report_filepath=s3_filepath, status_id=success_status_id).
                                    where(Report.id == report_id))
                    session.commit()
                    logger.info(f'Обработка отчета [{report[0]}] завершена')

                except Exception as err:
                    corrupted_count += 1
                    errors[str(report_id)] = str(err)
            logger.info('Обработка завершена')
        if corrupted_count:
            print(f'{corrupted_count}/{len(reports)} отчетов не удалось создать:')
            for k, v in errors.items():
                print('Отчет ' + k + ': ' + v)

        print('Новый поиск запросов через 60 сек...')
        time.sleep(60)


if __name__ == '__main__':
    main_cycle(2, 5)
    # with session_maker() as session:
    #     pr = Processor(session)
    #     pr.process_report(108, 'test', 1.5)
