
# 医療機関コード

## About
医療機関コード(施設コード)は、各地域の厚生局で管理、公開されているが、一方で全体の一覧が公開されているところは見つからなかった。(有料で購入できるサービスはある)。各地方厚生局のWebサイトから対象の医療機関一覧ファイルをダウンロードして、CSV形式でoutputする処理を作成する。

下記の地方厚生局のWebサイトを解析しているため、そのWebページが変更された場合、動作しなくなる可能性があります。  
最終確認日:2024-09-10  

最終実行のcsvは output/ にあります。[ダウンロードする](/output/202508_all_med_inst_cd.zip)


## 地方厚生局(link)

|地方厚生局|管轄地域|
|---|---|
|[北海道]("https://kouseikyoku.mhlw.go.jp/hokkaido/gyomu/gyomu/hoken_kikan/code_ichiran.html")|北海道|
|[東北](https://kouseikyoku.mhlw.go.jp/tohoku/gyomu/gyomu/hoken_kikan/itiran.html)|青森県,岩手県,宮城県,秋田県,山形県,福島県|
|[関東信越](https://kouseikyoku.mhlw.go.jp/kantoshinetsu/chousa/shitei.html)|茨城県,栃木県,群馬県,埼玉県,千葉県,東京都,神奈川県,新潟県,山梨県,長野県|
|[東海北陸](https://kouseikyoku.mhlw.go.jp/tokaihokuriku/gyomu/gyomu/hoken_kikan/shitei.html)|富山県,石川県,岐阜県,静岡県,愛知県,三重県|
|[近畿](https://kouseikyoku.mhlw.go.jp/kinki/tyousa/shinkishitei.html)|福井県,滋賀県,京都府,大阪府,兵庫県,奈良県,和歌山県|
|[中国](https://kouseikyoku.mhlw.go.jp/chugokushikoku/chousaka/iryoukikanshitei.html)|鳥取県,島根県,岡山県,広島県,山口県|
|[四国](https://kouseikyoku.mhlw.go.jp/shikoku/gyomu/gyomu/hoken_kikan/shitei/index.html)|香川県,徳島県,愛媛県,高知県|
|[九州](https://kouseikyoku.mhlw.go.jp/kyushu/gyomu/gyomu/hoken_kikan/index.html)|福岡県,佐賀県,長崎県,熊本県,大分県,宮崎県,鹿児島県,沖縄県|

## コード体系
上記のサイトで公開されている医療機関コード(施設コード)は7桁コード

- 9桁コード  
    都道府県番号(2桁)+7桁コード  
    DPCファイルのデータ提出に使われている.点数表コード医科(1)を含まない体系.

- 10桁コード  
    都道府県番号(2桁)+点数表コード(1桁;医科は1)+7桁コード  

## Output
{医療機関コード(9桁), 医療機関コード(7桁), 医療機関名称, 郵便番号, 住所}
のCSVファイル

(eg)
|医療機関コード(9)|医療機関コード(7)|医療機関名称|郵便番号|住所|
|---|---|---|---|---|
|010112489|0112489|医療法人 愛全病院|0050813|札幌市南区川沿１３条２丁目１番３８号|
|...|...|...|...|...|

最終実行(2025-08-09)のcsvは [ここから](/output/202508_all_med_inst_cd.zip) ダウンロードできます. 


# 位置参照情報
[国土交通省の位置参照情報](https://nlftp.mlit.go.jp/isj/index.html)
- 大字・町丁目レベル位置参照情報(0a)、街区レベル位置参照情報(0b)
- 0bをベースに不足分を0aから。複数ある場合、how?


## CHANGELOG

### August 9, 2025
- [東北厚生局のWebページ](https://kouseikyoku.mhlw.go.jp/tohoku/gyomu/gyomu/hoken_kikan/itiran.html)で医療機関コード一覧がTop配置でなくなった.またExcelファイルは都道府県ごとに1ファイルではなく、1ファイルでsheet/都道府県になった.

### April 7, 2022

- xlrdでxlsxが読めなくなったため、openpyxlを導入
    >xlrd 2.0.0 (11 December 2020): Remove support for anything other than .xls files.

- xlrdは不要に
    xls形式で公表する地方厚生局がなくなった(すべてxlsx形式になった)

