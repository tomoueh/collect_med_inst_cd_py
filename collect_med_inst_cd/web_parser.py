import logging
import re
from enum import Enum
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString

from .consts import (BRANCH_CYUGOKU, BRANCH_HOKAIDO, BRANCH_KANTO_SINETU,
                     BRANCH_KINKI, BRANCH_KYUSYU, BRANCH_SHIKOKU,
                     BRANCH_TOHOKU, BRANCH_TOKAI_HOKURIKU)


class WebPageType(Enum):
    TABLE = 1
    DIV = 2

class BranchWebpageParser:
    """
    厚生局の各WebPagをParseして医療機関コードFileのURLを取得する
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._branch_setting_dict = self.__init_branch_setting()

    def __init_branch_setting(self) -> dict:

        # 支部WebPageが更新されて、settingで分ける程度では同じparseで処理できなくなったら、個別classを作成すること

        href_excel_patt = re.compile(r'.+[xls|xlsx]$')
        href_zip_patt = re.compile(r'.+zip$')

        setting_dict = {
            # 北海道 table.class="m-table", 医科(病院)row,医科(診療所)row - excel
            BRANCH_HOKAIDO: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/hokkaido/gyomu/gyomu/hoken_kikan/code_ichiran.html",
                             {"class": "m-table"}, ("th", "医科"), href_excel_patt, None),
            # 東北  table.class="datatable", 医科row,医科(歯科併設)row - each_col=県, last_col=All県bundle(zip)
            BRANCH_TOHOKU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/tohoku/gyomu/gyomu/hoken_kikan/itiran.html",
                            {"class": "datatable"}, ("th", "医科"), href_zip_patt, None),
            # 関東信越 table.class="datatable", each_row=県,last_row=All県bundle(zip), col=医科,歯科
            BRANCH_KANTO_SINETU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/kantoshinetsu/chousa/shitei.html",
                                  {"class": "datatable"}, None, href_zip_patt, re.compile(r'^医科.*')),
            # 東海北陸  table.class="datatable", 医科row - each_col=県,last_col=All県bundle(zip)
            BRANCH_TOKAI_HOKURIKU: (WebPageType.DIV, "https://kouseikyoku.mhlw.go.jp/tokaihokuriku/newpage_00287.html",
                                    None, None, href_zip_patt, re.compile(r'医科')),
            # 近畿: table, 医科\n医科併設 row - each_col=県,last_col=All県bundle(zip)
            BRANCH_KINKI: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/kinki/tyousa/shinkishitei.html",
                           None, ("td", "医科"), href_zip_patt, None),
            # 四国: table.class="datatable", 医科row - each_col=県,last_col=All県bundle(zip)
            BRANCH_SHIKOKU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/shikoku/gyomu/gyomu/hoken_kikan/shitei/index.html",
                             {"class": "datatable"}, ("th", "医科"), href_zip_patt, None),
            # 中国: table.class="m-table", thなし, each_col=県,last_col=All県bundle(zip,a_text='医科')
            BRANCH_CYUGOKU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/chugokushikoku/chousaka/iryoukikanshitei.html",
                             {"class": "m-table"}, None, href_zip_patt, re.compile(r'^医科.*')),
            # 九州: table.class="datatable", each_td=県(zip.mix)
            BRANCH_KYUSYU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/kyushu/gyomu/gyomu/hoken_kikan/index_00006.html",
                            {"class": "datatable"}, None, href_zip_patt, None)
        }

        return setting_dict

    def extract_file_urls(self, branch_id: int) -> list:
        """
        Parse html of the branch page and get urls of med_list files(excel,zip)
        """

        # med_listがhtml page内で1つ目のtableでない特殊な構造の支局.2025/8から発生したのでパッチ的に対応
        NOT_FIRST_TABLE_BRANCHES = [BRANCH_TOHOKU]

        page_type, *_ = self._branch_setting_dict[branch_id]
        if page_type == WebPageType.TABLE:
            if branch_id in NOT_FIRST_TABLE_BRANCHES:
                return self._extract_urls_at_htmltables(branch_id)
            else:
                return self._extract_urls_at_first_htmltable(branch_id)
        else:
            return self._extract_urls_at_htmldiv(branch_id)

    def _extract_urls_at_first_htmltable(self, branch_id: int) -> list:
        """
        Parse the html first table of the branch page. get urls of med_list files(excel,zip)
        """

        _, url, table_class, _, _, _ = self._branch_setting_dict[branch_id]

        res = requests.get(url)
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        soup = BeautifulSoup(res.content, "html.parser")

        # find利用: html page内で1つ目のtableである前提
        table = soup.find("table", table_class) if table_class else soup.find("table")
        # self._logger.debug(table)
        href_l = self._extract_urls_from_a_htmltable(branch_id, table)

        if href_l:
            self._logger.debug(href_l)
        else:
            self._logger.warning(f"NOT get link. branch_id:{branch_id}")
        return href_l
    
    def _extract_urls_at_htmltables(self, branch_id: int) -> list:
        """
        Parse html tables of the branch page. get urls of med_list files(excel,zip)
        """

        _, url, table_class, _, _, _ = self._branch_setting_dict[branch_id]

        res = requests.get(url)
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        soup = BeautifulSoup(res.content, "html.parser")

        # html page内で1つ目のtableである前提
        tables = soup.find_all("table", table_class) if table_class else soup.find_all("table")
        for table in tables:
            href_l = self._extract_urls_from_a_htmltable(branch_id, table)
            if href_l:
                self._logger.debug(href_l)
                return href_l
        
        self._logger.warning(f"NOT get link. branch_id:{branch_id}")
    
    def _extract_urls_from_a_htmltable(self, branch_id: int, table: NavigableString) -> list:
        """
        Parse a html table and get urls of med_list files(excel,zip)
        """

        _, url, _, child_of_tr_attr, href_patt, a_str = self._branch_setting_dict[branch_id]

        # self._logger.debug(table)
        href_l = []
        tr_l = table.find_all("tr")
        for tr in tr_l:
            if child_of_tr_attr:
                children = tr.findChildren(child_of_tr_attr[0])
                if children and child_of_tr_attr[1] in children[0].text.replace(' ', '').replace('\u3000', ''):
                    links = tr.find_all("a", string=a_str, href=href_patt) if a_str else tr.find_all(
                        "a", href=href_patt)
                    if links:
                        # self._logger.debug(links)
                        href_l += [urljoin(url, link.get("href")) for link in links]
            else:
                links = tr.find_all("a", string=a_str, href=href_patt) if a_str else tr.find_all("a", href=href_patt)
                if links:
                    href_l += [urljoin(url, link.get("href")) for link in links]

        return href_l

    def _extract_urls_at_htmldiv(self, branch_id: int) -> list:
        """
        Parse html divs of the branch page and get urls of med_list files(excel,zip)
        """

        _, url, _, _, href_patt, a_str = self._branch_setting_dict[branch_id]

        res = requests.get(url)
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        soup = BeautifulSoup(res.content, "html.parser")
        href_l = []
        li_l = soup.find_all("li")
        for li in li_l:
            links = li.find_all("a", string=a_str, href=href_patt) if a_str else li.find_all("a", href=href_patt)
            if links:
                href_l += [urljoin(url, link.get("href")) for link in links]

        self._logger.debug(href_l)
        return href_l
