# King Gnu記事｜一次資料と商品販売先の照合（2026-11-25）

目的：①原稿の正確性と、②WorkによるPochipp・アクセストレード収益カード実装の効率化。

## 現行の優先5商品

| 製品 | メーカー公式 | 国内個別販売ページ | 根拠・留意点 |
|---|---|---|---|
| BOSS OC-5 | https://www.boss.info/jp/products/oc-5/ | https://www.soundhouse.co.jp/products/detail/item/282806/ | オクターブペダル。旧稿のOC-3とは別型番、モードの仕様が異なる |
| Z.VEX Fuzz Factory Vexter | https://www.zvex.com/guitar-pedals/fuzz-factory-vexter-guitar-effects-pedal-2020 | https://www.soundhouse.co.jp/products/detail/item/86625/ | 「Vexter版」の個別商品を確認。通常版・縦型・Fat/7は別製品であり混同禁止 |
| Xotic XW-1 Wah | https://www.xotic.jp/effects/xotic-wah/ | https://www.soundhouse.co.jp/products/detail/item/199546/ | 足踏みワウ。JOYO JF-322オートワウと操作方法は異なる |
| Source Audio Collider SA263 | https://sourceaudio.net/products/collider/SA263 | https://www.soundhouse.co.jp/products/detail/item/275724/ | ディレイ＋リバーブ。メーカー品番SA263を確認 |
| BOSS GX-1 | https://www.boss.info/jp/products/gx-1/ | https://www.soundhouse.co.jp/products/detail/item/382525/ | 2026年1月24日発売。旧稿のGT-1はBOSS公式で「販売完了」と表示 |

GT-1 メーカー表示：https://www.boss.info/jp/products/gt-1/  
GX-1 メーカー／発売情報：https://www.roland.com/jp/news/1182/

## 写真と動画の扱い
- **5商品とも「メーカー公式ページに商品画像が存在する」ことと「本サイトへ転載許可がある」ことは異なる。** メーカー画像は無断コピーせず、Pochippがショップ・ASP規約上許可する正式商品画像から表示する。
- 現時点で公式YouTubeの動画URLを5商品それぞれ特定・動作検証したわけではない。動画を本文へ捏造して貼らない。優先は製品写真＋購入先。
- 実際のライブ演奏は、公式YouTubeの正規動画が特定できた場合のみ本文冒頭へ埋め込む。
- 必要に応じて商品動画への**公式ページのリンク**を配置。メーカー製品動画の画像抽出・無断転載は禁止。

## 収益リンクの実装条件
1. サウンドハウスの上記は**通常の直接商品URL**。アクセストレードfroglinkが正しくURL変換するか、WordPress実ページ上で検証が必要。
2. もしも経由のAmazon・楽天・Yahooは、ユーザーがPochippの設定ID一致を確認済み。ただし**ASPの個別提携承認・ID保存・商品カード発行・実際のショップ遷移**は②Workが検査する。
3. Pochipp正規商品カード（商品写真、正しい型番、該当ショップへの成果リンク）を記事内の5商品紹介の直下に挿入する。
4. 価格・在庫は随時変わるため、記事への固定金額の掲載は実確認・日付付きでのみ。
5. Public GitHubにASPの管理用コード、サイト固有のキー、WordPress内部管理画面HTMLは保存しない。

## 記事での表現と根拠レベル
この商品リストは「King Gnuの音を参考にした**編集部独自の購入候補**」であり、**本人機材リストではない**。曲別の各製品採用も実際の録音使用を断定していない。掲載時は本文冒頭・各商品で誤認しない。

## ⓪管理としての判断
現行GT-1の推薦は停止しGX-1へ差し替えた。旧記事のGT-1情報は削除せず、現行購入候補との区別を明記した。残るボトルネックは許諾に適合する商品画像とASPカード、およびWordPressスマホ実表示。
