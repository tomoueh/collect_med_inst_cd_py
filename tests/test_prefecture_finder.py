# -*- coding: utf-8 -*-

import unittest
import logging
from collect_med_inst_cd.consts import *
from collect_med_inst_cd.prefecture_finder import PrefectureFinder

class TestPrefectureFinder(unittest.TestCase):

    def test_find_prefecture_cd(self):
        pref_finder = PrefectureFinder()
        pref_cd = pref_finder.find_prefecture_cd('6900887')
        # self._logger.debug(f"pref_cd={pref_cd}")
        self.assertEqual(pref_cd, "32")

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
