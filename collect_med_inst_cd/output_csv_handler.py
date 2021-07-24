import logging
import os
import csv

class OutputCsvHandler:
    """
    OutputCsvHandler
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def clear_output_file(self, out_dir: str, single_file: str):
        if not os.path.exists(out_dir):
            return

        f_path = os.path.join(out_dir, single_file)
        if os.path.exists(f_path):
            os.remove(f_path)

    def output_csv(self, out_dir: str, filename: str, med_list: list) -> str:
        if not med_list:
            return ''

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        file_path = os.path.join(out_dir, filename)
        with open(file_path, 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(med_list)

        self._logger.debug(f"output csv: {file_path}")
        return file_path

    def output_csv_append(self, out_dir: str, filename: str, med_list: list) -> str:
        if not med_list:
            return ''

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        file_path = os.path.join(out_dir, filename)
        with open(file_path, 'a', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(med_list)

        return file_path
