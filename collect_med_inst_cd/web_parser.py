import logging
import re
from enum import Enum
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

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
            # 北海道 table.class="datatable", 医科(病院)row,医科(診療所)row - excel
            BRANCH_HOKAIDO: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/hokkaido/gyomu/gyomu/hoken_kikan/code_ichiran.html",
                             {"class": "datatable"}, ("th", "医科"), href_excel_patt, None),
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
                           None, ("th", "医科"), href_zip_patt, None),
            # 四国: table.class="datatable", 医科row - each_col=県(excel)
            BRANCH_SHIKOKU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/shikoku/gyomu/gyomu/hoken_kikan/shitei/index.html",
                             {"class": "datatable"}, ("th", "医科"), href_zip_patt, None),
            # 中国: table.class="datatable", thなし, each_col=県,last_col=All県bundle(zip,a_text='医科')
            BRANCH_CYUGOKU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/chugokushikoku/chousaka/iryoukikanshitei.html",
                             {"class": "datatable"}, None, href_zip_patt, re.compile(r'^医科.*')),
            # 九州: table.class="datatable", each_td=県(zip.mix)
            BRANCH_KYUSYU: (WebPageType.TABLE, "https://kouseikyoku.mhlw.go.jp/kyushu/gyomu/gyomu/hoken_kikan/index_00006.html",
                            {"class": "datatable"}, None, href_zip_patt, None)
        }

        return setting_dict

    def extract_file_urls(self, branch_id: int) -> list:
        """
        Parse html of the branch page and get urls of med_list files(excel,zip)
        """

        page_type, *_ = self._branch_setting_dict[branch_id]

        if page_type == WebPageType.TABLE:
            return self._extract_urls_at_htmltable(branch_id)
        else:
            return self._extract_urls_at_htmldiv(branch_id)

    def _extract_urls_at_htmltable(self, branch_id: int) -> list:
        """
        Parse html table of the branch page and get urls of med_list files(excel,zip)
        """

        _, url, table_class, child_of_tr_attr, href_patt, a_str = self._branch_setting_dict[branch_id]

        res = requests.get(url)
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        soup = BeautifulSoup(res.content, "html.parser")
        table = soup.find("table", table_class) if table_class else soup.find("table")
        # self._logger.debug(table)
        href_l = []
        tr_l = table.find_all("tr")
        for tr in tr_l:
            if child_of_tr_attr:
                children = tr.findChildren(child_of_tr_attr[0])
                if children and child_of_tr_attr[1] in children[0].text:
                    links = tr.find_all("a", string=a_str, href=href_patt) if a_str else tr.find_all(
                        "a", href=href_patt)
                    if links:
                        # self._logger.debug(links)
                        href_l += [urljoin(url, link.get("href")) for link in links]
            else:
                links = tr.find_all("a", string=a_str, href=href_patt) if a_str else tr.find_all("a", href=href_patt)
                if links:
                    href_l += [urljoin(url, link.get("href")) for link in links]

        self._logger.debug(href_l)
        return href_l

    def _extract_urls_at_htmldiv(self, branch_id: int) -> list:
        """
        Parse html divs of the branch page and get urls of med_list files(excel,zip)
        """

        _, url, table_class, child_of_tr_attr, href_patt, a_str = self._branch_setting_dict[branch_id]

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
