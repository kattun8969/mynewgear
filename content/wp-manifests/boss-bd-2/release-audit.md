# BD-2完成見本｜公開前監査（2026-11-26）

## 内容・検証
- 正式モデル：BOSS **BD-2 Blues Driver**。BD-2W / BD-2-B50Aと区別。
- BOSS公式一次資料： https://www.boss.info/jp/products/bd-2/
- 比較対象一次資料： https://www.boss.info/jp/products/sd-1/ 、 https://www.boss.info/jp/products/od-3/ 、 https://www.boss.info/jp/products/bd-2w/
- 販売参考ページ（通常リンクであり成果リンクではない）： https://www.soundhouse.co.jp/products/detail/item/20704/
- 著者の実機使用を捏造せず、メーカー資料に基づいた購入ガイドとする。
- 比較の結論：指先の強弱→BD-2、中域→SD-1、低域/サステイン→OD-3。
- 価格・在庫は短期変動するため、レビュー本文では確定表記しない。
- 目標読者：1台目を検討中の初心者／既存歪みとの差分を調べたい人。

## 画像
- アイキャッチ候補：オリジナル作画の青いペダル風ビジュアル（**実製品写真ではない**）。文字「BD-2は買い？」「音作り・SD-1／OD-3比較」。
- 別途、BOSS公式写真を無断転載しない。商品そのものの写真は許諾済みのPochippカードから表示。
- WPメディアライブラリへの画像登録・アイキャッチ設定は未実装。スマホで文字が途切れないか必ず確認。
- 文字入り画像は検索者に訴求する補助表現であり、商品外観の正確性の根拠とはしない。

## 商品成果リンク
- [x] Pochipp **BOSS BD-2 Blues Driver** の登録投稿ID **1293** をREST読み取りで確認（通常モデル名に一致）
- [ ] Amazon/楽天/Yahoo：もしも経由の成果リンクが実際に正しい検索商品/商品URLへ飛ぶか確認
- [ ] サウンドハウス：アクセストレードの提携済みリンクを確認（通常のSoundHouse公開URLとは区別）
- [ ] 実際の登録済みPochipp IDが判明した場合のみ `[pochipp id="整数"]` を本文の比較表直後・まとめ直前に追加
- [ ] 商品カードにBD-2Wや限定版が混ざらないことを確認
- **IDやASPの秘密値はGitHubに書かない。** 必要ならGitHub Secrets／WP内設定で管理。

## 内部リンク
- [ ] /vivie-callion
- [ ] /beginner-ef-drive-1
- [ ] /yoasobi-assh
- [ ] /friedman-be-od
- [ ] /ovaltone-34xtoreme
- [ ] /source-audio-sa263-collider
それぞれ本番ページで404がないか、アンカーテキストが内容と一致するかチェック。

## WordPress
- すでにWP「確認用」の下書きID 1322 がある。
- GitHub `content/wp-manifests/boss-bd-2/source.md` 更新→ActionsのMarkdown HTML変換→上記下書きへ自動反映。
- 本番公開ページとは分離。SEOパーマリンク未確定のため公開モードに移行しない。
- 最終チェック：SANGOのPC 1280px・iPhone SE 320/375px、表の横スクロール、H1の重複、PR表記、商品画像、動画、スマホ商品ボタン、関連記事。
- **現状：文章と比較情報の編集版は準備できたが、商品カード・画像・表示検証が未完了。公開承認しない。**


## 2026-11-26 実施済み検証（公開前）
- [x] BD-2本文を公式仕様に基づく購入ガイドに再編集（PR #34、GitHub main）。
- [x] WPプレビュー投稿ID1322に更新。REST GETでstatus=draft。
- [x] Pochipp登録商品ID1293の投稿タイトルがBOSS BD-2 Blues DriverであることをRESTで確認。
- [x] WP RESTのrendered HTMLでショートコード展開あり、未展開の `[pochipp id="1293"]` なし。
- [x] レンダリングから画像5件、リンク23件、もしも系5リンク・アクセストレード系1リンクの**存在**を検知。**成果計測や型番一致を検証済みとするものではない**。
- [x] 原稿内関連記事6件（CALLION、初心者比較、YOASOBI、Friedman、Ovaltone、Collider）の公開URLがアクセスできることを確認。
- [ ] 購入カード内で全リンクが正しいBD-2通常版を表示することを画面で確認。
- [ ] 文字入りアイキャッチ候補をWPメディアに登録し、実製品写真と混同しない注記を整理。
- [ ] PC／320px／375pxで見た目確認。Pochippカードとテーブルが横にはみ出さないこと。
- [ ] 記事の正式スラッグ・新規記事／既存記事更新を決定し、公開前チェック。


## 2026-11-26　BD-2アイキャッチ・HTML QA完了

- [x] PR #35 を main にマージ。初回はActions Python 3.14とPillow 11.1の非互換によるビルド失敗を確認。
- [x] GitHub ActionsのPythonを3.12に固定して再実行、成功。
- [x] **投稿ID1322の非公開下書き**にオリジナルの日本語アイキャッチをメディアID **1329** として設定。
- [x] WordPress REST APIで投稿status=`draft`、添付画像は`image/png`・1600×900・altテキストありを確認。
- [x] 記事HTMLの比較表2つに横スクロールラッパーを実装。最初のH1はWP記事タイトル側だけで表示し、本文H1重複なし。
- [x] Pochipp登録商品1293のコードはレンダリング済み。未展開ショートコードなし。
- [x] 無効な仮リンク（#、javascript等）はゼロ。記事内リンク6パスと外部ドメインを抽出。
- [ ] **実ブラウザでのPC/iPhone SE表示**（カード位置、画像の読める大きさ、リストの段組）を確認。
- [ ] もしも／アクセストレード各ボタンを実際に開き、**BD-2通常版**の型番・販売先・報酬条件を確認。自動アクセスで成果リンクをクリックしてテストしない。
- [ ] WP実記事公開の可否（新規記事URL・必要なら既存URL整理）と正式アイキャッチの採用を決定。

GitHub Actions成功報告: https://github.com/kattun8969/mynewgear/issues/13#issuecomment-7167169283

**この段階で公開記事を変更していない。**
