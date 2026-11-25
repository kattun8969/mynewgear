# GitHubだけでWordPressを更新する｜まいにゅーぎあー

## 対象と公開権限
- WordPress: https://mynewgear.cyou/（ConoHa WING／SANGO子テーマ）。
- GitHub: kattun8969/mynewgear。**公開リポジトリにWPパスワード・APIキー・SSH秘密鍵・成果IDをコミットしない。**
- 記事の作成・プレビュー・公開とタグ設定は **WordPress REST API + GitHub Actions + WPアプリケーションパスワード**。
- プラグインのアップロードは別の **SSH/rsync手動実行Actions**。標準のREST APIは一般にサーバーのテーマ／プラグインファイルを直接更新する用途ではない。
- **SANGO子テーマを上書きするワークフローは未実装**。親テーマ、子テーマに対し中途半端なファイル群を丸ごと同期しない。PR #9はWP側検証後に安全な差分適用。

## 1. 必要なGitHub Secrets
GitHub → Settings → Secrets and variables → Actions → New repository secret

| Secret名 | 設定内容 |
|---|---|
| MNG_WP_SITE_URL | https://mynewgear.cyou |
| MNG_WP_USERNAME | API専用のWordPressユーザー名（投稿編集可能な権限のみ） |
| MNG_WP_APP_PASSWORD | WordPressのユーザープロフィールから生成した**アプリケーションパスワード** |
| MNG_WP_SSH_HOST | ConoHa側SSH接続先ホスト名（プラグインデプロイを使うときだけ） |
| MNG_WP_SSH_USER | SSHのデプロイ用ユーザー（同上） |
| MNG_WP_SSH_PRIVATE_KEY | SSH公開鍵認証の秘密鍵の内容（同上） |
| MNG_WP_SSH_KNOWN_HOSTS | SSHホストの検証済み公開鍵行（同上） |
| MNG_WP_REMOTE_PLUGINS_PATH | /.../wp-content/plugins のサーバー絶対パス（同上） |

**決してチャットやIssueへ秘密値を貼り付けない。** GitHub UIで直接登録する。REST APIの認証をサーバー・セキュリティプラグインが遮断している場合は、WordPress側の制限の再設定が必要。無闇にサイト全体の防御を解除しない。

## 2. デプロイ環境の安全設定
- GitHub Settings → Environmentsで `wp-production` を作成。プラン・公開/非公開リポジトリの利用条件に応じて**Required reviewers、デプロイブランチ main の制限**を付ける。
- GitHub Actionsの `wordpress-rest-sync.yml` は `workflow_dispatch` の手動実行のみ。mode=`check`（秘密不要）、`preview`（下書きコピー）、`taxonomy`（タグ作成・追加）、`publish`（本番更新）の4種。
- 本番更新は `main` ブランチ＋入力 `PUBLISH` が必要。可能なら `wp-production` の承認者も必ず設定。環境を作っただけでは承認ルールは付きません。
- GitHub Actions → MyNewGear WordPress REST sync → Run workflow から実行。

## 3. 初めての接続テスト（まだ未実行）
1. PRをレビューして main にマージ。workflow_dispatch はmainで利用できるようにしておく。
2. `mode=check`、`manifest=content/wp-manifests/samples/post-example.json` → JSON・HTMLのローカル検証。WP未接続。
3. `mode=preview`、同じmanifest → WordPressへ**確認用の非公開下書き**を新規登録。既存記事は上書きされない。
4. `mode=taxonomy`、`manifest=content/wp-manifests/taxonomy/discovery-tags.json` → 欲しい音と予算のタグを作成し、根拠のある既存4記事にタグを追加。**本文・カテゴリー・元タグは削除しない**。
5. 検索結果とタグの表示を確認。ここまでは本番記事の本文を書き換えずテストできる。

## 4. 記事の差し替え
- リライト原稿を `content/wp-manifests/<記事>/article.html` に保存。元の書き手の実機体験や広告、写真の差分を保持する。MarkdownはそのままRESTのHTMLとして投稿しない。
- 同じフォルダにJSON manifestを作成。`kind=post`, `slug`, `post_id`, `title`, `content_file`, `publish_ready=false` を設定。
- `preview` では `mng-preview-<slug>` に独立した下書きを保存し、**元の公開記事はそのまま**。
- 差分とASP、画像、SANGOスマホ表示の確認後に `publish_ready=true`。本番 `publish` 実行では同じslugの既存記事を明示的なpost_idで更新。
- 予期せぬ記事改変を検出したいときは `expected_modified_gmt` をmanifestに記載。WPの最新変更時刻と一致しなければ中断。
- 元記事を消したり投稿URLを変える処理は設けていない。WP側のリビジョン機能やサーバーバックアップは別に保持。

## 5. カテゴリー・タグの発見型ナビ
**カテゴリーは主題（エフェクター・ギター・音作り）、タグは選び方（音色・予算）**として分ける。価格は変動するので、予算タグは実際に掲載記事に現行の購入候補があるときだけ付与する。

| TOPボタン | タグのslug | 初期状態 |
|---|---|---|
| 軽い歪み | sound-light-drive | CALLION記事にタグ追加予定 |
| 迫力のある歪み | sound-heavy-drive | Friedman / Ovaltone記事に追加予定 |
| ファズ | sound-fuzz | 該当記事検証待ち |
| ディレイ・残響 | sound-delay-reverb | PLETHORA X5記事に追加予定 |
| マルチエフェクター | sound-multi-effects | PLETHORA X5記事に追加予定 |
| 1万円前後 | budget-around-10000 | 比較記事に対応商品追加後に紐付け |
| 3万円前後 | budget-around-30000 | 比較記事に対応商品追加後に紐付け |
| 5万円前後 | budget-around-50000 | 比較記事に対応商品追加後に紐付け |

- `wp-plugin/mng-discovery-tags/` は `[mng_discovery mode="sound"]` と `[mng_discovery mode="budget"]` を提供。
- タグに公開済み記事が1件以上あればアーカイブへリンク。記事が0件ならクリック不能な「準備中」表示。**空の検索結果や仮リンクに誘導しない**。
- 現行TOPは旧固定リンクを使っているため、上記ショートコードへの差し替えとプラグイン有効化は別途必要。最初の段階はGitHubでの準備まで。

## 6. GitHubのみでプラグインを更新する方法（SSHが使える場合）
- Actions → MyNewGear plugin deploy via SSH で `plugin=discovery`（タグナビ）または `weekly-picks`（週替わり表示）を選択。
- 最初に `action=dry-run` で接続/転送予定の差分確認。実行には設定済みSSHキーと接続先の検証済みホスト鍵が必要。
- 確認後 `action=upload`＋`confirmation=DEPLOY` で対象のプラグインフォルダだけ更新。**WordPressで有効化する作業は別**（UI、またはWP-CLIが許可されていれば追加実装可能）。
- テーマファイルと他プラグインを更新しないよう対象を明示している。既存のPochippやSANGOファイルに上書きしない。
- ConoHaのSSH権限/パス構成は未確認。SSHが使えない場合はここを実行せずWordPressプラグインZIPを使う。

## 完了している範囲 / まだ必要な範囲
**GitHub：** Actions設定・安全なREST投稿スクリプト・タグ定義・タグ導線プラグインの初版。
**未完了：** WP認証Secrets登録、REST認証の実接続、SSH確認、WordPressでのプラグイン有効化、元TOPのショートコード差し替え、公開URLとPC/スマホ表示テスト。
みんなの期待値は別のGitHubリポジトリ・WPサイトなので **認証情報やURLを共有しない**。連携方式は共通化できるが、サイトごとに独立したSecretsとデプロイ権限を使う。