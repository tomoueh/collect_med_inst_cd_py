import logging
import unittest

from collect_med_inst_cd.consts import *
from collect_med_inst_cd.excel_parser import ExcelParser


class TestExcelParser(unittest.TestCase):

    def test_parse_hokaido(self):
        parser = ExcelParser()
        excel_f = r".\tmp_data\000213687.xlsx"
        parser.parse(BRANCH_HOKAIDO, excel_f)

    def test_parse_shikoku(self):
        parser = ExcelParser()
        excel_f = r".\tmp_data\000155002.xls"
        parser.parse(BRANCH_SHIKOKU, excel_f)

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
