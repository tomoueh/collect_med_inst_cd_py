# -*- coding: utf-8 -*-

from typing import Callable
import logging
import os
import re
import csv
import zipfile
import shutil
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from .consts import BRANCH_ALL, BRANCH_LIST, BRANCH_KYUSYU
from .web_parser import BranchWebpageParser
from .excel_parser import ExcelParser

class MedInstCdCrawler:
    """
    MedicalInstitutionCdCrawler
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._web_parser = BranchWebpageParser()
        self._excel_parser = ExcelParser()

        # 九州のzipは医科、歯科、薬局のxlsxがbundle. 医科のみを対象
        self._zipfile_filter = {BRANCH_KYUSYU: re.compile(r'.+_ika_.*[xls|xlsx]$')}

    def download_cd_files(self, branch_id: int, dl_dir: str):
        """
        Download files that have med_inst_cds from the branch page
        """

        # download only. no need callback
        self._fetch_med_inst_cd(branch_id, dl_dir, None, '')

    def run(self, branch_id: int, out_dir: str = './output'):
        """
        Get med_inst_cd list from the branch page
        """

        self._fetch_med_inst_cd(branch_id, dl_dir='./tmp_data', callback=self._get_med_list_from_file, out_dir=out_dir)

    def _fetch_med_inst_cd(self, branch_id: int, dl_dir: str, callback: Callable[[int, int, str, str], None], out_dir: str):

        if branch_id == BRANCH_ALL:
            for b_id in BRANCH_LIST:
                self._logger.debug(f"..branch-{b_id} begin")
                self._fetch_med_inst_cd(b_id, dl_dir, callback, out_dir)
        else:
            file_urls = self._web_parser.extract_file_urls(branch_id)
            if file_urls:
                # clear out_dir at first
                if callback:
                    self._clear_output_dir_of(branch_id, out_dir)

                for i, f_url in enumerate(file_urls):
                    saved_file = self._download_to(f_url, dl_dir)
                    if saved_file:
                        if callback:
                            callback(branch_id, i+1, saved_file, out_dir)
                    else:
                        self._logger(f"can not download file: {f_url}")

    def _get_med_list_from_file(self, branch_id: int, p_seq: int, file_path: str, out_dir: str):

        re_patt_excel = re.compile(r'.+[xls|xlsx]$')

        if re.match(r'.+zip$', file_path):
            unzip_dir = self._zip_extract(file_path)
            counter = 1
            re_patt = self._zipfile_filter[branch_id] if branch_id in self._zipfile_filter else re_patt_excel
            for f in os.listdir(unzip_dir):
                f_path = os.path.join(unzip_dir, f)
                if os.path.isfile(f_path) and re_patt.match(f):
                    med_l = self._excel_parser.parse(branch_id, f_path)
                    if med_l:
                        f_name = f"{branch_id}_{p_seq}_{counter}_med_inst_cd.csv"
                        self._output_csv(out_dir, f_name, med_l)
                        counter += 1
        elif re_patt_excel.match(file_path):
            med_l = self._excel_parser.parse(branch_id, file_path)
            if med_l:
                f_name = f"{branch_id}_{p_seq}_med_inst_cd.csv"
                self._output_csv(out_dir, f_name, med_l)

    def _clear_output_dir_of(self, branch_id: int, out_dir: str):
        if not os.path.exists(out_dir):
            return

        for f in os.listdir(out_dir):
            f_path = os.path.join(out_dir, f)
            if os.path.isfile(f_path) and re.match(r'^'+str(branch_id)+r'_[.\w]+$', f):
                os.remove(f_path)

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

        return ''

    def _zip_extract(self, zipfile_path: str) -> str:
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
                        info.filename = f"dl_{counter}{ext}"
                        counter += 1
                    zfile.extract(info, unzip_dir)
        return unzip_dir

    def _output_csv(self, out_dir: str, filename: str, med_list: list) -> str:
        if not med_list:
            return ''

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        file_path = os.path.join(out_dir, filename)
        with open(file_path, 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(med_list)

        self._logger.debug(f"output csv: {file_path}")
        return file_path
