# Campus Palette

公開アプリ：https://sp5e7xr9-dev.github.io/campus-palette/

ソース：https://github.com/sp5e7xr9-dev/campus-palette

年度は2026→2025→2024の新しい順で表示します。大学公式の入試結果を、出典付きのカードとグラフで確認する無料の静的Webアプリです。React / TypeScript / Vite / Tailwind CSS / Recharts と Python を使用しています。ログイン・有料API・データベースは不要です。

## 最初に使う

ビルド済みの `dist/` を同梱しています。Python 3 があればNodeのインストール前でも試せます。

```bash
cd campus-palette
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

ブラウザで http://127.0.0.1:4173/ を開いてください。Macでは `ローカルで開く.command` の実行でも起動できます。終了はターミナルで Control+C。HTMLをダブルクリックする file:// での起動には対応していません。

これはこのMac専用のローカルURLです。娘さんの端末で開くための公開URLは、下のGitHub Pages手順で発行します。

## 収録範囲（2026年11月19日更新）

14大学・1066件、公式数値5870セル（算出倍率を除く）を収録。全大学・全年度・全方式の完全版ではありません。

| 大学 | 対象年度 | 収録範囲 |
| --- | --- | --- |
| 新潟・埼玉・弘前・岩手・山形・帯広畜産 | 2024〜2026 | 一般選抜等の原本掲載募集単位（大学ごとに得点区分が異なる） |
| 秋田 | 2024〜2026 | 原本画像と照合した26募集単位のみ |
| 福島 | 2025・2026 | 公表資料で照合した一般選抜の総合最低点 |
| 東京都立・宇都宮 | 2024〜2026 | 一般選抜の原本掲載募集単位。宇都宮は農学部改組前後を区別 |
| 宮城 | 2026 | 学群一括の一般選抜 |
| 東京薬科 | 2024・2026 | 生命科学部一般選抜30募集単位の得点と人数 |
| 千葉 | 2026 | 看護学部前期のみ。2024・2025年度全学PDFは取得失敗で確認待ち |
| 東北 | 2024〜2026 | 理・工・農の本学傾斜配点と合格者平均。理は後期を含む。学部一括の公表 |

弘前の共通テスト平均は傾斜配点前、宮城は学群一括、岩手は第1志望合格者のみです。東京薬科B/T方式は得点補正あり。未収録・非公表を0にせず「入手不可」と表示し、出典・理由を確認できます。

検証記録：[初回追加](docs/2026-11-18-expansion.md) ／ [追加Excelの照合](docs/2026-11-18-workbook-import.md) ／ [欠損の再調査](docs/2026-11-19-recheck.md)。添付Excelの「確認済み」をそのまま承認せず、公式PDF/HTMLとの照合後に承認しています。原本表からの機械抽出を含み、全セルを人が目視確認した意味ではありません。

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

取得後は `.cache/candidate.json` に**確認待ち**で保存します。失敗時は `.cache/last-error.json` を作成し、公開JSONを上書きしません。原本PDF・HTMLは `.cache/sources/` にローカル保存し、Git管理・公開・成果物添付から除外します。

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

本リポジトリはGitHub Pagesで公開済みです。GitHub上でテスト・ビルド・HTTPS公開の成功を確認しています。次は、別のリポジトリへ移して公開する場合の手順です。現在の公開アプリを使うだけなら、この設定は不要です。

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

`docs/検証結果.md` に検証内容を記録しています。iPhone/iPad相当の画面幅で検証し、GitHub Actions上のテスト・ビルド・公開と、公開URLでの両大学の実データ表示・出典リンクを確認しました。iOS実機Safariの操作と実際のホーム画面インストールは実機での確認が必要です。

比較は最大3大学対応ですが、収録した14大学から選択できます。リアルタイム収集のAPIはなく、未取得項目を閲覧者が直接収集することはできません。管理者の定期収集・確認で更新します。大学ごとの公開範囲が異なるため、全項目・全年度・全方式の数値がそろうことは保証していません。

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
