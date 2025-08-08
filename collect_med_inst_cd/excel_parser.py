import logging
import os
import re

import openpyxl


class ExcelParser:
    """
    Parse the medical-institude excel file of the Kouseikyoku.
    """

    def parse(self, branch_id: int, file_path: str) -> list:
        """
        Parse the excel file and get med_inst_cd list
        """

        setting = {'col_no': 0, 'col_med_cd': 1, 'col_inst_name': 2, 'col_address': 3}
        # if branch_id in (BRANCH_KYUSYU):
        #     setting = {'col_no': 2, 'col_med_cd': 6, 'col_inst_name': 10, 'col_address': 15}
        # else:
        #     setting = {'col_no': 0, 'col_med_cd': 1, 'col_inst_name': 2, 'col_address': 3}

        _, ext = os.path.splitext(file_path)
        parser = ExcelParserXlsx(setting)
        return parser.parse(file_path)


class ExcelParserXlsx:
    """
    Parse the Kouseikyoku excel xlsx file. Use openpyxl.
    """

    def __init__(self, setting: dict):
        self._logger = logging.getLogger(__name__)
        self._setting = setting
        self._val_cleaner = ValueCleaner()

    def parse(self, file_path: str) -> list:
        """
        Parse the excel file and get med_inst_cd list
        """

        self._logger.debug(f"parse excel begin: {file_path}")

        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet = wb.worksheets[0]
        # self._logger.debug(sheet.row_values(8))
        med_list = []
        for row in sheet.iter_rows():
            # check 項番col. 項番colのある行に医療機関コード,医療機関名,住所が入ってる
            cell_no = row[self._setting['col_no']].value
            if cell_no and cell_no.isdigit():

                med_cd = self._val_cleaner.parse_med_inst_cd(row[self._setting['col_med_cd']].value)
                inst_name = self._val_cleaner.parse_med_inst_name(row[self._setting['col_inst_name']].value)
                zip_cd, address = self._val_cleaner.parse_address(row[self._setting['col_address']].value)

                med_list.append([med_cd, inst_name, zip_cd, address])

        # self._logger.debug(med_list)
        return med_list

class ValueCleaner:
    """
    Clean each value of the Kouseikyoku excel file.
    """

    def parse_med_inst_cd(self, med_cd: str) -> str:

        if not med_cd:
            return ""

        cd = med_cd.split('\n')[0]
        # convert
        #  01,1047,8.. to 0110478
        #  01-1857-5 to 0118575
        #  01.1857.5 to 0118575
        cd = cd[:9].replace(',', '').replace(
            '-', '').replace('.', '').replace('・', '').replace(' ', '')

        return cd

    def parse_med_inst_name(self, med_inst_name: str) -> str:

        if not med_inst_name:
            return ""

        # Zenkaku-space to space
        inst_name = med_inst_name.replace('\u3000', ' ').strip()

        return inst_name

    def parse_address(self, address: str) -> tuple:

        if not address:
            return ("", "")

        # zip_cd, address
        addrs = address.split('\n', 1)
        if len(addrs) >= 2:
            zip_cd = addrs[0].lstrip('〒').replace('－', '').strip()
            addr = addrs[1].replace('\u3000', ' ').strip()
        else:
            addr = address.lstrip('〒').strip()
            m = re.match(r'^([0-9－]+)(.+)$', addr)
            if m:
                zip_cd = m.group(1).replace('－', '')
                addr = m.group(2).replace('\u3000', ' ').strip()
            else:
                # would be no zipcd
                zip_cd = ''
                addr = addr.replace('\u3000', ' ').strip()

        return (zip_cd, addr)
