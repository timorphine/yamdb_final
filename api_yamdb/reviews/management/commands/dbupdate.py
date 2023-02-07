import csv

from django.core.management.base import BaseCommand


class DbUpdate(BaseCommand):
    """Добавляет записи из csv-файлов в БД."""

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def main(self):
        self.stdout.write('== Импортируем CSV-файлы ==')

        with open(self.file_path, mode='r') as f:
            csv.DictReader(f)
