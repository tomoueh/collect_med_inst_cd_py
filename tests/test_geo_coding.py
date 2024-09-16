import logging
import re
import unittest

from collect_med_inst_cd.geo_coding import GeoCoding


class TestGeoCoding(unittest.TestCase):

    def test_create_file_wt_geo(self):
        geo = GeoCoding()
        geo._logger = self._logger
        med_file_path = r".\output\all_med_inst_cd.csv"
        geo.create_file_wt_geo(med_file_path, check_only=True)

    def test_map_address_point(self):
        geo = GeoCoding()
        geo._logger = self._logger
        geo._map_address_point()

    def test_convert2kansuji(self):
        geo = GeoCoding()
        val = geo._convert2kansuji("2")
        self.assertEqual(val, "二")

        val = geo._convert2kansuji("10")
        self.assertEqual(val, "十")

        val = geo._convert2kansuji("14")
        self.assertEqual(val, "十四")

        val = geo._convert2kansuji("27")
        self.assertEqual(val, "二十七")

        val = geo._convert2kansuji("37")
        self.assertEqual(val, "三十七")

        val = geo._convert2kansuji("80")
        self.assertEqual(val, "八十")

        val = geo._convert2kansuji("114")
        self.assertEqual(val, "百十四")

        val = geo._convert2kansuji("2300")
        self.assertEqual(val, "二千三百")

        val = geo._convert2kansuji("2345")
        self.assertEqual(val, "二千三百四十五")

        # self._logger.debug(val)

    def test_re_foo(self):

        for s in ["札幌市中央区南１条西１３丁目３１７番地１", "札幌市中央区宮の森１２３７番地１", "札幌市白石区本通２丁目南５番１０号", "深川市３条２５番１９号"]:
            m = re.match(r'(\S+[０-９]+丁目[北|南]?)\S*', s)
            if m:
                self._logger.debug(m.groups())
            else:
                m = re.match(r'(\S*[^０-９]+)(?=[０-９]+番)', s)
                if m:
                    self._logger.debug(m.groups())

    def test_re_foo2(self):

        for s in ["水戸市三の丸３－１２－４８", "水戸市双葉台３－３－１０", "水戸市双葉台１０", "水戸市袴塚３ー１ー１５", "水戸市宮町１の１の１"]:
            replaced = re.sub(r'(\S*[^０-９－ーの])+([０-９])+[－ーの]', r'\1\2丁目', s)
            self._logger.debug(replaced)

    def test_search_in_dict(self):

        geo_dict = {"深川市音江町": "1", "利尻郡利尻町沓形": "2", "阿寒郡鶴居村字雪裡原野": "3"}
        for s in ["深川市音江町字音江", "阿寒郡鶴居村字雪裡原野北", "利尻郡利尻町沓形字緑町"]:
            for k, v in geo_dict.items():
                if k in s:
                    self._logger.debug(f"{v}: {s}")
                    break

    def test__kansujinize_match_wrapper(self):
        geo = GeoCoding()
        for s in ["札幌市中央区南１条西１３丁目３１７番地１", "札幌市中央区宮の森１２３７番地１", "宮の森２３７番地", "宮の森２７番地"]:
            converted = re.sub(r'([０-９]+)', geo._kansujinize_match_wrapper, s)
            self._logger.debug(f"{converted}")

    def setUp(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)  # change the level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
