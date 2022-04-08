# -*- coding: utf-8 -*-

from typing import Callable
import logging
import os
import re
import zipfile
import shutil
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from .consts import BRANCH_ALL, BRANCH_LIST, BRANCH_KYUSYU
from .web_parser import BranchWebpageParser
from .excel_parser import ExcelParser
from .prefecture_finder import PrefectureFinder
from .output_csv_handler import OutputCsvHandler

class MedInstCdCrawler:
    """
    MedicalInstitutionCdCrawler
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._web_parser = BranchWebpageParser()
        self._excel_parser = ExcelParser()
        self._pref_finder = PrefectureFinder()
        self._csv_handler = OutputCsvHandler()

        # 九州のzipは医科、歯科、薬局のxlsxがbundle. 医科のみを対象
        self._zipfile_filter = {BRANCH_KYUSYU: re.compile(r'.+_ika_.*[xls|xlsx]$')}

    def download_cd_files(self, branch_id: int, dl_dir: str):
        """
        Download files that have med_inst_cds from the branch page
        """

        # download only. no need callback
        self._fetch_med_inst_cd(branch_id, dl_dir, None, '', False)

    def run(self, branch_id: int, out_dir: str = './output'):
        """
        Get med_inst_cd list from the branch page
        """

        output_file = "all_med_inst_cd.csv" if branch_id == BRANCH_ALL else f"{branch_id}_med_inst_cd.csv"
        self._csv_handler.clear_output_file(out_dir, output_file)

        self._fetch_med_inst_cd(branch_id, './tmp_data', self._output_med_list_from_file, out_dir, output_file)

    def _fetch_med_inst_cd(self, branch_id: int, dl_dir: str, output_handler: Callable[[int, int, str, str, str], None], out_dir: str, output_file: str):
        """
        Download files from each kouseikyoku.mhlw.go.jp sites and sum them up to csv.
        """

        if branch_id == BRANCH_ALL:
            for b_id in BRANCH_LIST:
                self._logger.debug(f"..branch-{b_id} begin")
                # call this recursively
                self._fetch_med_inst_cd(b_id, dl_dir, output_handler, out_dir, output_file)
        else:
            file_urls = self._web_parser.extract_file_urls(branch_id)
            if file_urls:
                for i, f_url in enumerate(file_urls):
                    saved_file = self._download_to(f_url, dl_dir)
                    if saved_file:
                        if output_handler:
                            output_handler(branch_id, i+1, saved_file, out_dir, output_file)
                    else:
                        self._logger(f"can not download file: {f_url}")

    def _output_med_list_from_file(self, branch_id: int, p_seq: int, file_path: str, out_dir: str, output_file: str):

        re_patt_excel = re.compile(r'.+[xls|xlsx]$')

        if re.match(r'.+zip$', file_path):
            unzip_dir = self._zip_extract(file_path)
            # specified pattern or excel pattern
            re_patt = self._zipfile_filter[branch_id] if branch_id in self._zipfile_filter else re_patt_excel
            for f in os.listdir(unzip_dir):
                f_path = os.path.join(unzip_dir, f)
                if os.path.isfile(f_path) and re_patt.match(f):
                    med_l = self._parse_file(branch_id, f_path)
                    if med_l:
                        self._csv_handler.output_csv_append(out_dir, output_file, med_l)

        elif re_patt_excel.match(file_path):
            med_l = self._parse_file(branch_id, file_path)
            if med_l:
                self._csv_handler.output_csv_append(out_dir, output_file, med_l)

    def _parse_file(self, branch_id: int, file_path: str) -> list:
        """
        Parse Excel file and create med_inst_cd list. Add 10digit med_inst_cd to each item of the list.
        """

        med_l = self._excel_parser.parse(branch_id, file_path)
        if med_l:
            # use first valid zip_cd
            pref_cd = ''
            retry = 8
            for med_item in med_l:
                zip_cd = med_item[2]
                if zip_cd:
                    pref_cd = self._pref_finder.find_prefecture_cd(zip_cd)
                    if pref_cd:
                        med_l = [[f"{pref_cd:0>2}{item[0]}"]+item for item in med_l]
                        break

                retry -= 1
                if retry <= 0:
                    break

            if not pref_cd:
                med_l = [[""]+item for item in med_l]

        return med_l

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

    def _zip_extract(self, zipfile_path: str) -> str:

        # file名をdirに
        unzip_dir = os.path.join(os.path.dirname(zipfile_path), os.path.splitext(os.path.basename(zipfile_path))[0])
        if os.path.exists(unzip_dir):
            shutil.rmtree(unzip_dir)

        with zipfile.ZipFile(zipfile_path) as zfile:
            counter = 1
            for info in zfile.infolist():
                # skip directory within the zipfile
                if not info.filename.endswith(r'/'):
                    if not re.match(r'^[a-zA-Z0-9\.-_]+$', info.filename):
                        # ファイル名が全角記号、全角スペース含まれてたりする、予測不可能.置き換えちゃう
                        # info.filename = info.filename.encode('cp437').decode('cp932')
                        _, ext = os.path.splitext(info.filename)
                        if not ext:
                            # extが文字化けファイル名から取得できないケースがあったので,,
                            splited = info.filename.split('.')
                            ext = f".{splited[-1]}"
                        info.filename = f"dl_{counter}{ext}"
                        counter += 1
                    zfile.extract(info, unzip_dir)
        return unzip_dir
