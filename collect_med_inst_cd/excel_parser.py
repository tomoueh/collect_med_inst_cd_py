# -*- coding: utf-8 -*-

import xlrd
import re
import logging
from .consts import BRANCH_HOKAIDO, BRANCH_TOKAI_HOKURIKU, BRANCH_KINKI

class ExcelParser:

    def parse(self, branch_id: int, file_path: str) -> list:
        """
        Parse the excel file and get med_inst_cd list
        """

        setting = {}
        if branch_id in (BRANCH_HOKAIDO, BRANCH_TOKAI_HOKURIKU, BRANCH_KINKI):
            setting = {'col_no': 0, 'col_med_cd': 1, 'col_inst_name': 2, 'col_address': 3}
        else:
            setting = {'col_no': 2, 'col_med_cd': 6, 'col_inst_name': 10, 'col_address': 15}

        parser = ExcelParserImpl(setting)
        return parser.parse(file_path)

class ExcelParserImpl:

    def __init__(self, setting: dict):
        self._logger = logging.getLogger(__name__)
        self._setting = setting

    def parse(self, file_path: str) -> list:
        """
        Parse the excel file and get med_inst_cd list
        """

        self._logger.debug(f"parse excel begin: {file_path}")

        # https://xlrd.readthedocs.io/en/latest/
        wb = xlrd.open_workbook(file_path)
        for sheet in wb.sheets():
            # self._logger.debug(sheet.row_values(8))
            med_list = []
            for nrow in range(sheet.nrows):
                # check 項番col
                cell_no = sheet.cell_value(nrow, self._setting['col_no'])
                if cell_no and cell_no.isdigit():

                    med_cd = sheet.cell_value(nrow, self._setting['col_med_cd'])
                    med_cd = med_cd.split('\n')[0]
                    # convert
                    #  01,1047,8.. to 0110478
                    #  01-1857-5 to 0118575
                    #  01.1857.5 to 0118575
                    med_cd = med_cd[:9].replace(',', '').replace(
                        '-', '').replace('.', '').replace('・', '').replace(' ', '')

                    inst_name = sheet.cell_value(nrow, self._setting['col_inst_name'])
                    # Zen-space to space
                    inst_name = inst_name.replace('\u3000', ' ')

                    cell_addr = sheet.cell_value(nrow, self._setting['col_address'])
                    # zip_cd, address
                    addr = cell_addr.split('\n', 1)
                    if len(addr) == 2:
                        zip_cd = addr[0].lstrip('〒').replace('－', '')
                        address = addr[1].replace('\u3000', ' ').strip()
                    else:
                        cell_addr = cell_addr.lstrip('〒')
                        m = re.match(r'^([0-9－]+)(.+)$', cell_addr)
                        if m:
                            zip_cd = m.group(1).replace('－', '')
                            address = m.group(2).replace('\u3000', ' ').strip()
                        else:
                            # would be no zipcd
                            zip_cd = ''
                            address = cell_addr.replace('\u3000', ' ').strip()

                    med_list.append([med_cd, inst_name, zip_cd, address])

            # self._logger.debug(med_list)
            return med_list
