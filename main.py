import logging

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from database.db import session_maker
from database.models import Report
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

    def get_reports(self):
        """
        Метод получает идентификаторы запросов для формирования отчетов из БД
        :return: список идентификаторов
        """
        stmt = select(Report.id).where(and_(Report.status_id == 2, Report.to_delete == False))
        reports_to_process = self.session.execute(stmt).scalars().all()
        return reports_to_process

    def process_report(self, data):
        new_report = ReportGenerator(**data)
        new_report.write_general_params()
        new_report.save_report('test.docx')

    def get_data_content(self, report_id: int) -> dict:
        """
        Загрузка данных из S3-хранилища
        :param report_id:
        :return: словарь - имя параметра: csv-данные
        """
        logger.info('Скачивание данных...')
        path = self.csv_path_template.replace('{{REPORT_ID}}', str(report_id))

        result = {}
        obj_names = [obj.object_name for obj in storage.get_list_objects(path)]

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

with session_maker() as session:
    processor = Processor(session)
    data = processor.get_data_content(101)
    data['header'] = 'test'
    data['outlier_rate'] = 1.5
    processor.process_report(data)
