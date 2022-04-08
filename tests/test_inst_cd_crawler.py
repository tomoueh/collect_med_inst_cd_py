# -*- coding: utf-8 -*-

import unittest
import logging
from collect_med_inst_cd.consts import *
from collect_med_inst_cd.inst_cd_crawler import MedInstCdCrawler

class TestMedInstCdCrawler(unittest.TestCase):

    def test_run_all(self):
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_ALL)

    def test_run_one(self):
        crawler = MedInstCdCrawler()
        # crawler.run(BRANCH_TOHOKU)
        # crawler.run(BRANCH_KANTO_SINETU)
        # crawler.run(BRANCH_SHIKOKU)
        # crawler.run(BRANCH_CYUGOKU)
        crawler.run(BRANCH_KYUSYU)

    def test_run_each(self):
        crawler = MedInstCdCrawler()
        for b_id in BRANCH_LIST:
            crawler.run(b_id)

    def test_zip_extract(self):
        crawler = MedInstCdCrawler()
        # zip_f = r".\tmp_data\ze_sitei_ika_R0207.zip"
        zip_f = r".\tmp_data\000236407.zip"
        crawler._zip_extract(zip_f)

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
