import logging
from typing import Sequence

from sqlalchemy import select, and_, Row
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
        self.target_files = {'текущая рк.csv': 'cur_rk', 'органический трафик.csv': 'org',
                             'группы по типу рк.csv': 'groups',
                             'все кампании.csv': 'campaigns', 'предыдущая рк.csv': 'prev_rk'}

    def get_reports(self) -> Sequence[Row[tuple]]:
        """
        Метод получает идентификаторы запросов для формирования отчетов из БД
        :return: список идентификаторов
        """
        logger.info('Поиск запросов для подготовки отчетов...')
        stmt = (
            select(Report.id, Product.name).
            join(Product, Report.product_id == Product.id).
            where(and_(Report.status_id == 2, Report.to_delete == False))
        )

        reports_to_process = self.session.execute(stmt).all()
        logger.info(f'Найдено {len(reports_to_process)} запросов, готовых к обработке')
        return reports_to_process

    def process_report(self, report_id: int, header: str, outlier_rate: float = 1.5):
        logger.info(f'Обработка отчета [{report_id}]...')
        data = self.get_data_content(report_id)
        if not data:
            return
        data['header'] = header
        data['outlier_rate'] = outlier_rate

        logger.info(f'Формирование файла...')
        new_report = ReportGenerator(**data)
        new_report.write_general_params()
        new_report.write_page_views()
        new_report.write_funnel_graph_section()
        new_report.write_outliers_section()
        new_report.write_groups_section()
        new_report.save_report(f'reports/test{report_id}.docx')
        logger.info('Файл сформирован')
        return True

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


# if __name__ == '__main__':
#     while True:
#         with session_maker() as session:
#             processor = Processor(session)
#             reports_to_process = pr(session)
#
#         print('спим 60 сек')
#         time.sleep(60)

corrupted_count = 0
with session_maker() as session:
    processor = Processor(session)
    # processor.process_report(101, 1.5)
    reports = processor.get_reports()
    for report in reports:
        succues = processor.process_report(report[0], report[1])
        if not succues:
            corrupted_count += 1
        logger.info(f'Обработка отчета [{report[0]}] завершена')

    logger.info(f'{corrupted_count} отчетов не удалось создать')
