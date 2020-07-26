# -*- coding: utf-8 -*-

import argparse
import logging
from collect_med_inst_cd.consts import BRANCH_ALL
from collect_med_inst_cd.inst_cd_crawler import MedInstCdCrawler
from collect_med_inst_cd.web_parser import BranchWebpageParser
from collect_med_inst_cd.excel_parser import ExcelParser


parser = argparse.ArgumentParser()
parser.add_argument('-b', '--branch', type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8],
                    help='指定なし:全部, 1:北海道,2:東北,3:関東信越,4:東海北陸,5:近畿,6:四国,7:中国,8:九州')
parser.add_argument('-d', '--dl', action='store_true', help='ファイルのダウンロードのみ')
parser.add_argument('--output', type=str, default='./output', help='出力ディレクトリ')
args = parser.parse_args()
branch_id = args.branch
if not branch_id:
    branch_id = BRANCH_ALL

crawler = MedInstCdCrawler()
if args.dl:
    crawler.download_cd_files(branch_id, args.output)
else:
    crawler.run(branch_id, args.output)
