# Campus Palette

大学公式の入試結果を、出典付きのカードとグラフで確認する無料の静的Webアプリです。React / TypeScript / Vite / Tailwind CSS / Recharts と Python を使用しています。ログイン・有料API・データベースは不要です。

## 最初に使う

ビルド済みの `dist/` を同梱しています。Python 3 があればNodeのインストール前でも試せます。

```bash
cd campus-palette
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

ブラウザで http://127.0.0.1:4173/ を開いてください。Macでは `ローカルで開く.command` の実行でも起動できます。終了はターミナルで Control+C。HTMLをダブルクリックする file:// での起動には対応していません。

これはこのMac専用のローカルURLです。娘さんの端末で開くための公開URLは、下のGitHub Pages手順で発行します。

## 収録範囲（2026年11月18日確認）

- 新潟大学：2024〜2026年度。公式データブック2025・2026・2027の入試結果と合格者得点。全10学部の掲載募集単位を対象にしています。
- 埼玉大学：2024〜2026年度。一般選抜の実施状況、合格者の総合最低点・総合平均点。全5学部の掲載募集単位を対象にしています。
- 346件の「大学・募集単位・選抜区分・入学年度」の組み合わせ。原本9PDF・24ページ、公式数値2,336セル。人数から算出した倍率は別に保存します。
- 新潟大学の合格点は共通テスト・個別試験が別々の値です。総合点は結果資料に確認できないため**入手不可**です。最低点同士を足し合わせていません。
- 埼玉大学の得点は**総合点**です。共通テスト・個別試験それぞれの合格者平均には転用しません。
- 募集要項の利用科目・科目別配点、受験者平均、埼玉大学の特別選抜はこの版では未照合・未収録です。原本にある可能性のある情報も、確認前は入手不可とします。
- 合格者数による非公表、段階評価、改組、募集単位の違いは補完しません。科目別配点の解析と、全選抜方式の網羅は今後の拡張対象です。

原本PDFと画像は配布していません。JSONは数値の事実を独自の構造で整理したものです。各大学の名称・ロゴ・資料の著作権を譲渡・再許諾するものではありません。公開運用時も大学の利用条件と取得制限を確認してください。

公式入口：

- [新潟大学 入試データブック](https://www.niigata-u.ac.jp/admissions/data/)
- [埼玉大学 年度別入試結果](https://www.saitama-u.ac.jp/entrance/exam_info/result/)
- [新潟大学 このサイトについて](https://www.niigata-u.ac.jp/sitepolicy/)
- [埼玉大学 このサイトについて](https://www.saitama-u.ac.jp/about/)

## 開発環境

Node.js 22以降、pnpm 11.25.0、Python 3.12以降を使用します。NodeやPythonのシステム設定を変更するスクリプトは含みません。

```bash
npm install -g pnpm@11.25.0
pnpm install --frozen-lockfile
pnpm dev
```

表示されたローカルURLを開きます。依存ライブラリの初回取得にはインターネット接続が必要です。

```bash
pnpm test
python3 -m unittest discover -s tests -p 'test_*.py' -v
pnpm build
pnpm preview
```

Pythonの公開データテストは標準ライブラリだけで実行できます。取得処理には次の追加依存が必要です。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/collect.py
```

## データ更新・確認・承認

収集と公開は分離しています。収集は `scripts/universities.json` の許可済みHTTPS公式URLだけを使用し、robots.txtを確認します。取得間隔は最低2秒、リダイレクト先も公式ホスト内に限定します。robots取得失敗・403・429・タイムアウト・レイアウト変更はエラーとして停止します。証明書検証は無効化しません。robots.txtが404の場合はルール指定なしとして扱います。取得元の利用条件を確認し、変更や禁止があれば収集設定から外してください。

取得後は `.cache/candidate.json` に**確認待ち**で保存します。失敗時は `.cache/last-error.json` を作成し、公開JSONを上書きしません。原本PDFは `.cache/sources/` にローカル保存し、Git管理・公開・成果物添付から除外します。

```bash
python scripts/collect.py
python scripts/review.py list
python scripts/review.py show --id 表示されたID
```

`show` に出る原本URLを開き、**大学・入学年度・学部・学科・区分・試験種別・各値・配点・人数**を確認します。ページ番号はPDFの1始まりのページ番号です。冊子内に印字されたページ番号とは1ページずれることがあります。

```bash
python scripts/review.py approve --id 対象ID --digest showで表示されたdigest --reviewer 管理者名
python scripts/review.py export
pnpm test
python -m unittest discover -s tests -p 'test_*.py' -v
pnpm build
```

`approve` はレコード単位で実行します。元PDFのSHA-256・対象ラベル・値・出典が変わると承認は失効し、`export` でその数値は欠損に戻ります。初期の承認は表構造・年度・得点順序・得点率・別PDF抽出エンジンでの数値所在を機械照合し、代表募集単位の原本画像も確認したものです。**全セルを人が目視照合したという意味ではありません。** 管理者による原本照合を追加する場合も同じCLIを利用できます。

新潟大学の「受験倍率」はこのアプリの「実質倍率」と定義が異なります。本アプリでは志願倍率＝志願者数÷募集人員、実質倍率＝受験者数÷合格者数として算出し、`kind: calculated` を付けています。原本の括弧内人数（内数）を足しません。表示は小数第2位まで、倍率の内部保存は小数第4位までです。得点率は同じ年度・同じ試験の得点÷満点で算出します。

## 自動収集

`.github/workflows/collect.yml` は毎月2日7:17頃（日本時間、GitHubの遅延あり）と手動実行で収集します。公開資料の確認待ちJSONとエラーログを7日間のActions成果物として保存します。PDF原本はActions成果物に含めません。

取得→機械検証→候補保存までは自動です。**変更内容の承認と公開JSONの更新は管理者が行います。** 原本の変更を無承認で公開する仕組みはありません。GitHub上の成果物を使う場合、ローカルで同じ `collect.py` を実行して原本を取得し、候補・digestを照合してください。

変更後の `public/data/admissions.json` と `scripts/approvals.json` を main にpushするとPages公開ワークフローが検証・ビルド・公開します。収集失敗時も既存の公開アプリは引き続き表示できます。公開リポジトリで長期間操作がない場合、GitHubがスケジュールを無効化することがあるため、Actions画面を確認してください。

## 大学の追加

1. `scripts/universities.json` に一意のid・大学名・よみがな・公式URL・利用条件URL・各年度の資料URLを追加します。
2. 資料の書式に応じて `scripts/parsers/大学ID.py` を作成します。既存書式と同じであれば同じparserを指定できます。parserの許可リストも `collect.py` で更新します。
3. `parse(paths, year, source)` から共通形式のレコードを返し、出典ページを各値に指定します。
4. 原本を確認し、テストと承認・exportを実行します。

設定を追加しただけで未解析の大学が対応済みになることはありません。10〜20大学にも同じ構造で拡張できます。異なる科目・集計単位の数値を推測で結合しないでください。

## 完全無料の公開（GitHub Pages）

2026年11月18日にGitHub公式ドキュメントを確認しました。GitHub Freeの**公開リポジトリ**でPagesが使えます。[料金条件と制限](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)では、公開サイト1GBまで、帯域月100GBのソフト制限などがあります。本アプリのサイズと月1回の収集は小規模な個人利用を想定しています。上限到達時は利用・更新を止めて調整し、有料プランへ自動移行するコードはありません。契約条件が将来変わる可能性はあります。

この納品物には公開設定とビルド済みファイルがありますが、GitHubリポジトリの作成・アカウントへのログイン・Pagesの有効化はまだ行っていません。接続ツールには新規リポジトリ作成とPages設定の機能がないため、次の操作をアカウントの所有者が行ってください。

1. GitHubにログインし、`campus-palette` という **Public** リポジトリを作ります。個人利用で広告・商取引を行わない構成を想定しています。
2. 本フォルダのソースをそのリポジトリのmainブランチへ登録します。`node_modules`・`.cache`・`dist` は登録しません。非公開ファイルや元PDFをアップロードしないでください。
3. Gitが使える場合は、このフォルダ内で次を実行します（OWNERを自分のGitHubユーザー名に置き換えます）。

```bash
git init -b main
git add .
git commit -m "Build Campus Palette with verified official admissions data"
git remote add origin https://github.com/OWNER/campus-palette.git
git push -u origin main
```

4. リポジトリの Settings → Pages → Build and deployment → Source を **GitHub Actions** にします。Environmentsで承認が設定されている場合は、公開実行時に所有者が承認します。
5. Actions → **Test and publish free GitHub Pages** → Run workflow を実行します。両ジョブが成功したら、deployジョブに表示される実際のHTTPS URLを開きます。予定URLは `https://OWNER.github.io/campus-palette/` です。これはまだ発行済みのURLではありません。
6. 公開した実際のURLを娘さんのSafariで開きます。

PWAのパスは相対指定なので、リポジトリ名付きのPagesでも動きます。HTTPSはPagesの標準URLで提供され、独自ドメインは不要です。カード情報・Apple ID・OpenAI APIキーは不要です。

## 娘さんのiPhone・iPad

公開URLをSafariで開く → 共有ボタン → **ホーム画面に追加** → 名前「Campus Palette」を確認して追加します。iPadでも同様です。大学名・よみがなで検索し、募集単位と区分を選びます。ハートでお気に入りを保存できます。数値をタップすると確認状態と公式原本へのリンクを表示します。

初回はオンラインで開いてください。一度読み込んだアプリとデータはService Workerで端末にキャッシュします。オフラインでは最後に読んだデータが表示されるため、設定画面の確認日を確認してください。ブラウザがキャッシュを削除した場合は再接続が必要です。お気に入りと履歴は端末ごとに保存され、同期はしません。Safariのプライベートモード・保存制限では永続保存できない場合があります。

## 検証と制約

`docs/検証結果.md` に検証内容を記録しています。iPhone/iPad相当の画面幅でローカルブラウザ検証を実施しました。iOS実機Safariの操作、実際のホーム画面インストール、GitHub Actions上の実行と公開URLはアカウント設定後の確認が必要です。

比較は最大3大学対応ですが、初期データは2大学なので現在選べるのは2大学です。リアルタイム収集のAPIはなく、未取得項目を閲覧者が直接収集することはできません。管理者の定期収集・確認で更新します。大学ごとの公開範囲が異なるため、全項目・全年度・全方式の数値がそろうことは保証していません。

## 構成

```text
src/                  画面・型・欠損処理・フロントエンドテスト
public/data/          公開用JSON（数値ごとの状態・出典）
public/               PWAマニフェスト、Service Worker、アイコン
scripts/collect.py    公式資料の取得、大学別解析、検証
scripts/core.py       共通レコードと検証
scripts/parsers/      大学ごとの表解析
scripts/review.py     内容digestによる確認・承認・公開JSONの生成
scripts/approvals.json 初期承認のdigestと確認方法
.github/workflows/    Pages公開と月次収集
 tests/               データ分離、承認失効、欠損、取得失敗のテスト
 docs/                日本語の検証結果
 dist/                起動・公開可能なビルド済みアプリ（ZIP納品のみ）
```
