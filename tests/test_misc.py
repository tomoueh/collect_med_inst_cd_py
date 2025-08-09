import logging
import unittest

from collect_med_inst_cd.consts import *


class TestMisc(unittest.TestCase):

    def test_pref_cd_dict(self):
        for pref_cd in ["1", "2", "10", "21", "33", "44", "48"]:
            self._logger.debug(f"pref:{pref_cd},{pref_cd_dict.get(pref_cd, 'unknown')}")

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
