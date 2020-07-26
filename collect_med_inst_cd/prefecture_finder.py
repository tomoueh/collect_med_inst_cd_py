# -*- coding: utf-8 -*-

import logging
import json
import requests

class PrefectureFinder:

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def find_prefecture_cd(self, zip_cd: str) -> str:
        """
        Get the prefecture cd of Japan with zip_cd
        """

        # http://zipcloud.ibsnet.co.jp/doc/api
        url = "https://zipcloud.ibsnet.co.jp/api/search"
        params = {"zipcode": zip_cd}
        res = requests.get(url, params)

        if res.status_code == 200:
            # self._logger.debug(res.text)
            if res.text:
                result_dict = json.loads(res.text)
                if result_dict.get('status') == 200:
                    addr_l = result_dict.get('results')
                    if addr_l:
                        pref_cd = addr_l[0].get('prefcode')
                        self._logger.debug(f"found pref_cd={pref_cd}")
                        return pref_cd
                    else:
                        self._logger.warn(f"NOT found pref_cd: zip_cd={zip_cd}")
                else:
                    self._logger.error(
                        f"zipcloud res-json: status={result_dict.get('status')},message={result_dict.get('message')}")
            else:
                self._logger.error("zipcloud res-json: None")

        else:
            self._logger.error(f"zipcloud http-response status_code={res.status_code}")

        return ""
