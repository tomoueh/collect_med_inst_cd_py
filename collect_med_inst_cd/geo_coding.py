import csv
import logging
import os
import pickle
import re

import pandas as pd
import requests

from .output_csv_handler import OutputCsvHandler


class GeoCoding:

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_file_wt_geo(self, med_file_path: str, check_only=False):
        """

        """

        self._logger.debug(f"begin parsing file: {med_file_path}")
        if os.path.isfile(med_file_path):

            # geo_point_df = self._map_address_point()
            geo_point_dicts = self._address_point_to_dict(self._map_address_point())

            result_l = []
            with open(med_file_path, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    medInstAddress = re.sub(r'^北海道|東京都|(京都|大阪)府|\S{2,3}県', '', row[4]).replace(' ', '')
                    # To漢数字
                    t_address = re.sub(r'([０-９]+)', self._kansujinize_match_wrapper, medInstAddress)
                    point_v = self._find_geo_point_of_each_address_by_dict(t_address, geo_point_dicts)
                    if (not point_v):
                        t_address = re.sub(r'^(\S+?)([０-９])+[－ー―の]', r'\1\2丁目', medInstAddress)
                        t_address_wo_cyome = re.sub(r'([０-９]+)', self._kansujinize_match_wrapper, t_address)
                        point_v = self._find_geo_point_of_each_address_by_dict(t_address_wo_cyome, geo_point_dicts)

                    if (point_v):
                        result_l.append([*row, point_v[0], point_v[1]])
                    else:
                        self._logger.warn(f"Not found geo point. address:{row[4]}")
                        result_l.append([*row, "", ""])

            if (not check_only):
                file_name = os.path.splitext(os.path.basename(med_file_path))[0]
                file_name = f"{file_name}_wt_geo.csv"
                csv_h = OutputCsvHandler()
                csv_h.output_csv(os.path.dirname(med_file_path), file_name, result_l)

    def _address_alias(self) -> list:
        return [("", ""), ("の", "ノ"), ("ノ", "の"), ("ヶ", "ケ"), ("ケ", "ヶ"),
                ("桜", "櫻"), ("通り", "通"), ("桧山", "檜山")];

    def _find_geo_point_of_each_address_by_dict(self, medInstAddress: str, t_dicts: tuple) -> tuple:
        for i, addressText in enumerate([medInstAddress, medInstAddress.replace("大字", "")]):
            if (i != 0 and addressText == medInstAddress):
                continue

            for (fromText, toText) in self._address_alias():
                # convert address in each case
                t_address = addressText
                if (fromText != "" and fromText in addressText):
                    t_address = t_address.replace(fromText, toText)
                    # t_address = addressText.translate(str.maketrans(conv))
                    if (t_address == addressText):
                        continue
                # find t_address
                for t_dict in t_dicts:
                    geo_points = self._find_geo_point_of_each_address_impl_by_dict(t_address, t_dict)
                    if (geo_points):
                        return geo_points
        return ()

    def _find_geo_point_of_each_address_impl_by_dict(self, medInstAddress: str, t_dict: dict) -> tuple:
        """
        Find Geolonia point of address.
        """
        # filtered_keys = [key for key in t_dict.keys() if medInstAddress.startswith(key)]
        filtered_dict = {k: v for (k, v) in t_dict.items() if medInstAddress.startswith(k)}
        if (len(filtered_dict) == 0):
            return ()
        if (len(filtered_dict) == 1):
            return list(filtered_dict.values())[0]
        if (len(filtered_dict) >= 2):
            # find longest match one
            maxlen = max(len(k) for k in filtered_dict)
            found_dict = {k: v for (k, v) in filtered_dict.items() if len(k) == maxlen}
            return list(found_dict.values())[0]

        return ()

    # def _find_geo_point_of_each_address_by_df(self, medInstAddress: str, geo_point_df: pd.DataFrame) -> tuple:
    #     for i, addressText in enumerate([medInstAddress, medInstAddress.replace("大字", "")]):
    #         if (i != 0 and addressText == medInstAddress):
    #             continue

    #         for conv in ({"": ""}, {"の": "ノ"}, {"ノ": "の"}, {"ヶ": "ケ"}, {"ケ": "ヶ"}, {"桜": "櫻"}):
    #             t_address = addressText
    #             if (list(conv.keys())[0] != ""):
    #                 t_address = addressText.translate(str.maketrans(conv))
    #                 if (t_address == addressText):
    #                     continue
    #             # find t_address
    #             geo_points = self._find_geo_point_of_each_address_impl_by_df(t_address, geo_point_df)
    #             if (geo_points):
    #                 return geo_points
    #     return ()

    # def _find_geo_point_of_each_address_impl_by_df(self, medInstAddress: str, geo_point_df: pd.DataFrame) -> tuple:
    #     """
    #     Find Geolonia point of address.
    #     """
    #     for search_col in ["address", "address_wo_oaza", "address_called"]:
    #         filtered_geo_point_df = geo_point_df[geo_point_df[search_col].map(
    #             lambda x: x != "" and medInstAddress.startswith(x))]
    #         if (len(filtered_geo_point_df) == 0):
    #             continue
    #         if (len(filtered_geo_point_df) == 1):
    #             return (filtered_geo_point_df["latitude"].values.tolist()[0], filtered_geo_point_df["longitude"].values.tolist()[0])
    #         if (len(filtered_geo_point_df) >= 2):
    #             # find that matches longest one
    #             max_len = filtered_geo_point_df[search_col].str.len().max()
    #             found_df = filtered_geo_point_df[filtered_geo_point_df[search_col].str.len() == max_len]
    #             if (len(found_df) >= 2 and search_col != "address_called"):
    #                 not_called_df = found_df[found_df["address_called"].str.len() == 0]
    #                 if (len(not_called_df) > 0):
    #                     found_df = not_called_df
    #             return (found_df["latitude"].values.tolist()[0], found_df["longitude"].values.tolist()[0])

    #     return ()

    # def create_file_wt_geo_old(self, med_file_path: str):
    #     """

    #     """

    #     self._logger.debug(f"begin parsing file: {med_file_path}")
    #     if os.path.isfile(med_file_path):

    #         geo_point_dict = self._address_point_to_dict(self._map_address_point())

    #         # 1.'丁目'があれば、そこまで
    #         # 2.'番地'の前まで, '番'の前まで
    #         re_patterns = (re.compile(r'(\S+[０-９]+丁目[北|南]?)\S*'),
    #                        re.compile(r'(\S*[^０-９]+)(?=[０-９]+番地)'), re.compile(r'(\S*[^０-９]+)(?=[０-９]+番)'))
    #         #    re.compile(r'([^０-９]+)(?=[０-９]+)'))
    #         result_l = []
    #         with open(med_file_path, 'r', encoding="utf-8") as f:
    #             reader = csv.reader(f)
    #             for row in reader:
    #                 address = row[4]

    #                 for patt in re_patterns:
    #                     m = patt.match(address)
    #                     if m:
    #                         address = m.groups()[0]
    #                         break

    #                 # To漢数字
    #                 address = re.sub(r'([０-９]+)', self._kansujinize_match_wrapper, address)

    #                 if address in geo_point_dict:
    #                     point_v = geo_point_dict[address]
    #                     result_l.append([*row, point_v[0], point_v[1]])
    #                 else:
    #                     matched = False
    #                     # 住の江,山ノ手,旭ヶ丘,
    #                     for conv in ({"の": "ノ"}, {"ノ": "の"}, {"ヶ": "ケ"}, {"ケ": "ヶ"}):
    #                         s = address.translate(str.maketrans(conv))
    #                         if s in geo_point_dict:
    #                             point_v = geo_point_dict[s]
    #                             result_l.append([*row, point_v[0], point_v[1]])
    #                             matched = True
    #                             break

    #                     # if not matched:
    #                     #     # geo_point_dictのaddressが短いCase
    #                     #     for addr, p in geo_point_dict.items():
    #                     #         if addr in address:
    #                     #             result_l.append([*row, p[0], p[1]])
    #                     #             matched = True
    #                     #             break

    #                     if not matched:
    #                         self._logger.debug(f"orig={row[4]}: converted={address}")
    #                         result_l.append([*row, "", ""])

    #         # self._logger.debug(result_l[:5])

    #         file_name = os.path.splitext(os.path.basename(med_file_path))[0]
    #         file_name = f"{file_name}_wt_geo.csv"
    #         csv_h = OutputCsvHandler()
    #         csv_h.output_csv(os.path.dirname(med_file_path), file_name, result_l)

    def _map_address_point(self, forced_fetch=False) -> pd.DataFrame:
        """
        Retrieve Geolonia data and return as pd.DataFrame
        """

        # Geolonia住所データ
        # https://geolonia.github.io/japanese-addresses/
        # https://github.com/geolonia/japanese-addresses

        pickl_f = r".\tmp_data\geolonia.pickl"

        if forced_fetch or not os.path.isfile(pickl_f):

            self._logger.debug("download Geolonia data")
            # Geolonia住所データ
            url = "https://raw.githubusercontent.com/geolonia/japanese-addresses/master/data/latest.csv"
            # geo_f = self._download_to(url, r".\tmp_data")
            geo_f = r".\tmp_data\latest.csv"

            df = pd.read_csv(geo_f, encoding='utf-8', dtype={"小字・通称名": "string"})
            self._logger.debug(df.to_string(max_rows=5))

            for l_v in ["緯度", "経度"]:
                df[l_v] = df[l_v].round(6)
            df["oaza_name"] = df["大字町丁目名"].str.replace("（大字なし）", "")
            df["address"] = df["市区町村名"] + df["oaza_name"]
            df.rename(columns={'緯度': 'latitude', '経度': 'longitude'}, inplace=True)
            # add the without-oaza address
            df["address_wo_oaza"] = ""
            df["address_wo_oaza"] = df["address_wo_oaza"].mask(
                df["oaza_name"].str.startswith("大字"), df["市区町村名"] + df["oaza_name"].str.replace("大字", "", 1))
            df["address_wo_oaza"] = df["address_wo_oaza"].mask(
                df["oaza_name"].str.startswith("字"), df["市区町村名"] + df["oaza_name"].str.replace("字", "", 1))
            # add the so-called address
            df["address_called"] = df["小字・通称名"].where(df["小字・通称名"].isnull(), df["市区町村名"] + df["小字・通称名"])
            df["address_called"].fillna("", inplace=True)

            addressDf = df[["address", "address_wo_oaza", "address_called", "latitude", "longitude"]]
            # no duplicated, meanless.
            # addressDf.drop_duplicates(subset=["address", "address_wo_oaza",
            #                           "address_called"], keep='last').reset_index(drop=True, inplace=True)

            # save as pickle file
            with open(pickl_f, 'wb') as handle:
                pickle.dump(addressDf, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            self._logger.debug("get data from pickle file")

            with open(pickl_f, 'rb') as handle:
                addressDf = pickle.load(handle)

        # self._logger.debug(addressDf.to_string(max_rows=30))
        self._logger.debug(f"addressDf size: {len(addressDf)}")

        return addressDf

    def _address_point_to_dict(self, df: pd.DataFrame) -> tuple:
        """
        create dict(address, tuple(lat,lng)) from pd.DataFrame
        """

        wo_called_df = df[df["address_called"].str.len() == 0]
        # 1.address-unique
        address_unique = wo_called_df.copy().drop_duplicates("address")
        address_unique["point_v"] = list(map(tuple, address_unique[["latitude", "longitude"]].values))
        # self._logger.debug(address_unique.head())

        # 2.address_wo_oaza-unique
        address_wo_oaza_unique = wo_called_df[wo_called_df["address_wo_oaza"].str
                                              .len() >= 1].copy().drop_duplicates("address_wo_oaza")
        address_wo_oaza_unique["point_v"] = list(map(tuple, address_wo_oaza_unique[["latitude", "longitude"]].values))

        # 3.address_called
        address_called = df[df["address_called"].str.len() >= 1].drop_duplicates("address_called")
        address_called["point_v"] = list(map(tuple, address_called[["latitude", "longitude"]].values))

        return (dict(zip(address_unique["address"], address_unique["point_v"])),
                dict(zip(address_wo_oaza_unique["address_wo_oaza"], address_wo_oaza_unique["point_v"])),
                dict(zip(address_called["address_called"], address_called["point_v"])))

    def _download_to(self, url: str, dl_dir: str) -> str:

        if not os.path.exists(dl_dir):
            os.mkdir(dl_dir)

        filename = url.split('/')[-1]
        savepath = os.path.join(dl_dir, filename)
        if os.path.exists(savepath):
            os.remove(savepath)

        res = requests.get(url, stream=True)
        with open(savepath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        return savepath

    def _kansujinize_match_wrapper(self, m: re.Match) -> str:
        if not m.group():
            return ""

        return self._kansujinize(str(m.group()))

    # 数字半角[0-9] 0x30～0x39
    # 数字全角[０-９] 0xFF10～0xFF19
    ZEN_NUM = "".join(chr(0xff10 + i) for i in range(9))
    HAN_NUM = "".join(chr(0x30 + i) for i in range(9))

    NUM_ZEN2HAN = str.maketrans(ZEN_NUM, HAN_NUM)

    def _kansujinize(self, num_text: str) -> str:
        """
        Make Numner letter to Kanji-Number
        """

        han_num = num_text.translate(self.NUM_ZEN2HAN)
        return self._convert2kansuji(han_num)

    def _convert2kansuji(self, han_num: str):
        suji = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        kugiri = ["", "十", "百", "千"]
        # tani = ["", "万", "億", "兆", "京", "垓", "𥝱", "穣", "溝", "澗", "正", "載", "極", "恒河沙", "阿僧祇", "那由他", "不可思議", "無量大数"]

        num = list(map(int, list(han_num)))
        kansuji = []

        for k, v in zip(range(len(num)), reversed(num)):
            keta = []
            keta.append(suji[v if v >= 2 else 0 if k % 4 else v])
            keta.append(kugiri[k % 4 if v > 0 else 0])
            # keta.append((tani[0 if k % 4 else int(k/4) if any(list(reversed(num))
            #                                                   [k:(k+4 if len(num) >= (k+4) else len(num))]) else 0]))
            kansuji.append("".join(keta))

        kansuji = "".join(reversed(kansuji))

        return kansuji
