import unittest
import logging
from collect_med_inst_cd.consts import *
from collect_med_inst_cd.web_parser import BranchWebpageParser

class TestBranchWebpageParser(unittest.TestCase):

    def test_parse_tokai_hokuriku(self):
        parser = BranchWebpageParser()
        urls = parser.extract_file_urls(BRANCH_TOKAI_HOKURIKU)

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
