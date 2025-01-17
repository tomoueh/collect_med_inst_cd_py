import logging
import re
import unittest
import pandas as pd

from collect_med_inst_cd.geo_coding import GeoCoding


class TestGeoCoding(unittest.TestCase):

    def test_create_file_wt_geo(self):
        geo = GeoCoding()
        geo._logger = self._logger
        med_file_path = r".\output\all_med_inst_cd.csv"
        # med_file_path = r".\tests\test_med_inst_cd.csv"
        geo.create_file_wt_geo(med_file_path, check_only=True)

    def test_map_address_point(self):
        geo = GeoCoding()
        geo._logger = self._logger
        df = geo._map_address_point(forced_fetch=True)
        # check
        self._logger.debug(df.to_string(max_rows=10))
        # has address_wo_oaza
        self._logger.debug(df[df["address_wo_oaza"].str.len() > 0].to_string(max_rows=10))
        # has address_called
        self._logger.debug(df[df["address_called"].str.len() > 0].to_string(max_rows=10))

        # for t_address in ["弘前市泉田１３３７番", "長野市問御所町１３３７番地イの４"]:
        #     filtered_df = df[df["address_called"].map(
        #         lambda x: x != "" and t_address.startswith(x))]
        #     self._logger.debug(f"--{t_address}: {'hit!' if len(filtered_df) > 0 else 'not found'}")
        #     if len(filtered_df) > 0:
        #         self._logger.debug(filtered_df.to_string())

    def test_address_point_to_dict(self):
        geo = GeoCoding()
        geo._logger = self._logger
        dict1, dict2, dict3 = geo._address_point_to_dict(geo._map_address_point(forced_fetch=True))
        self._logger.debug(f"size={len(dict1),len(dict2),len(dict3)}")
        self._logger.debug(list(dict1.items())[:5])
        self._logger.debug(list(dict2.items())[:5])
        self.assertIn("川越市大袋新田", dict2)
        self.assertIn("茅部郡鹿部町鹿部", dict2)
        # self._logger.debug(dict2.get("川越市大袋新田", "Not found"))
        # self._logger.debug(dict2.get("茅部郡鹿部町鹿部", "Not found"))
        self._logger.debug(list(dict3.items())[:5])

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

    def test_re_sub_cyome(self):

        for s in ["川口市前川１－１－５５メディパーク川口前川２－Ｃ", "水戸市三の丸３－１２－４８", "水戸市双葉台３－３－１０",
                  "水戸市双葉台１０", "水戸市袴塚３ー１ー１５", "水戸市宮町１の１の１"]:
            replaced = re.sub(r'^(\S+?)([０-９])+[－ー―の]', r'\1\2丁目', s)
            # replaced = re.sub(r'(\S*[^０-９－ー―])+(?:([０-９])+[－ー―の])', r'\1\2丁目', s)
            self._logger.debug(replaced)
    
    def test_remove_todofuken(self):
        for s in ["北海道札幌市西区発寒八条１２丁目１番１号", "茨城県水戸市内原２丁目１番地", "京都府京都あいうえお",
                  "北海道北広島市Ｆビレッジ", "広島市あいうえお"]:
            replaced = re.sub(r'^北海道|東京都|(京都|大阪)府|\S{2,3}県', '', s)
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
