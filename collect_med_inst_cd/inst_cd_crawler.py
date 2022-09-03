import logging
import os
import re
import shutil
import zipfile
from typing import Callable
from urllib.parse import urljoin

import requests

from .consts import BRANCH_ALL, BRANCH_KYUSYU, BRANCH_LIST
from .excel_parser import ExcelParser
from .output_csv_handler import OutputCsvHandler
from .prefecture_finder import PrefectureFinder
from .web_parser import BranchWebpageParser


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
                # call this recursively
                self._fetch_med_inst_cd(b_id, dl_dir, output_handler, out_dir, output_file)
        else:
            self._logger.debug(f"..branch-{branch_id} begin")
            file_urls = self._web_parser.extract_file_urls(branch_id)
            if file_urls:
                for i, f_url in enumerate(file_urls):
                    saved_file = self._download_to(f_url, dl_dir)
                    if saved_file:
                        self._logger.debug(f"downloaded: {saved_file}")
                        if output_handler:
                            output_handler(branch_id, i+1, saved_file, out_dir, output_file)
                    else:
                        self._logger.warn(f"can not download file: {f_url}")

    def _output_med_list_from_file(self, branch_id: int, p_seq: int, file_path: str, out_dir: str, output_file: str) -> None:

        re_patt_excel = re.compile(r'.+[xls|xlsx]$')

        if re.match(r'.+zip$', file_path):
            unzip_dir = self._zip_extract(file_path)
            # specified pattern or excel pattern
            re_patt = self._zipfile_filter[branch_id] if branch_id in self._zipfile_filter else re_patt_excel

            self._output_file_in_dir(branch_id, unzip_dir, re_patt, out_dir, output_file)

        elif re_patt_excel.match(file_path):
            med_l = self._parse_file(branch_id, file_path)
            if med_l:
                self._logger.debug(f"output_csv_append: {file_path}")
                self._csv_handler.output_csv_append(out_dir, output_file, med_l)

    def _output_file_in_dir(self, branch_id: str, dir_path: str, file_filter: re.Pattern, out_dir: str, output_file: str) -> None:

        for f in os.listdir(dir_path):
            f_path = os.path.join(dir_path, f)
            if os.path.isdir(f_path):
                # call this recursively
                self._output_file_in_dir(branch_id, f_path, file_filter, out_dir, output_file)

            elif os.path.isfile(f_path) and file_filter.match(f):
                med_l = self._parse_file(branch_id, f_path)
                if med_l:
                    self._logger.debug(f"output_csv_append: {f_path}")
                    self._csv_handler.output_csv_append(out_dir, output_file, med_l)

    def _parse_file(self, branch_id: int, file_path: str) -> list:
        """
        Parse Excel file and create med_inst_cd list. Add 10-digit med_inst_cd to each item of the list.
        """

        # fileはprefecture単位の前提
        med_l = self._excel_parser.parse(branch_id, file_path)
        if med_l:
            # Find the prefecture-cd using first valid zip_cd, add med_inst_cd(9 digit) with its prefecture-cd.
            # Must be one file for one prefecture.
            pref_cd = ''
            retry = 8
            for med_item in med_l:
                zip_cd = med_item[2]
                if zip_cd:
                    pref_cd = self._pref_finder.find_prefecture_cd(zip_cd)
                    if pref_cd:
                        # Add med_inst_cd(9 digit) at the first column
                        med_l = [[f"{pref_cd:0>2}{item[0]}"]+item for item in med_l]
                        break

                retry -= 1
                if retry <= 0:
                    self._logger.warn(f"can not find the prefecture cd: {file_path}")
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
