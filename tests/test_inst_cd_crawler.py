# -*- coding: utf-8 -*-

import unittest
import logging
from collect_med_inst_cd.consts import *
from collect_med_inst_cd.inst_cd_crawler import MedInstCdCrawler

class TestMedInstCdCrawler(unittest.TestCase):

    def test_run_all(self):
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_ALL)

    def test_run_hokaido(self):
        self._logger.debug("start: HOKAIDO")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_HOKAIDO)

    def test_run_tohoku(self):
        self._logger.debug("start: TOHOKU")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_TOHOKU)

    def test_run_kanto_sinetu(self):
        self._logger.debug("start: KANTO_SINETU")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_KANTO_SINETU)

    def test_run_tokai_hokuriku(self):
        self._logger.debug("start: TOKAI_HOKURIKU")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_TOKAI_HOKURIKU)

    def test_run_kinki(self):
        self._logger.debug("start: KINKI")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_KINKI)

    def test_run_cyugoku(self):
        self._logger.debug("start: CYUGOKU")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_CYUGOKU)

    def test_run_shikoku(self):
        self._logger.debug("start: SHIKOKU")
        crawler = MedInstCdCrawler()
        crawler.run(BRANCH_SHIKOKU)

    def test_run_kyusyu(self):
        self._logger.debug("start: KYUSYU")
        crawler = MedInstCdCrawler()
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

        self._logger = logging.getLogger("collect_med_inst_cd")
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
