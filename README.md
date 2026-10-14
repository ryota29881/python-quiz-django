# PYTHON LEARNING QUIZ

Python・Tkinterで制作したクイズアプリを、Djangoを使用したWebアプリケーションへ発展させた作品です。

「Pythonの知識をクイズ形式で学ぶ」という元の作品の目的を維持しながら、Webアプリとして利用できるように、ユーザー認証・成績履歴・管理画面などを追加しています。

## 作品概要

- **4択クイズ**：カテゴリ・難易度を選択して最大5問に回答
- **コード作成クイズ**：Pythonコードを入力して自動判定
- **解答・解説表示**：回答後に正誤と解説を表示
- **結果表示**：クイズ終了後に正解数・正答率・ランクを表示
- **ユーザー機能**：新規登録、ログイン、ログアウト
- **マイページ**：ログインユーザーの成績・クイズ履歴を表示
- **Django Admin**：問題、選択肢、コード問題、クイズ履歴を管理
- **レスポンシブ対応**：PC・スマートフォンの画面幅に対応
- **ASTによるコード判定**：コード作成クイズの入力内容をPythonのASTで解析

## 技術スタック

- Python
- Django（`requirements.txt` に記載されたバージョン）
- SQLite
- HTML / CSS
- Django Templates
- Python AST（コード判定）

## ディレクトリ構成

```text
python-quiz-django/
├── config/                  # Djangoプロジェクト設定
├── quiz/                    # 4択クイズ・認証・履歴・マイページ
├── code_quiz/               # コード作成クイズ
├── question_data/           # 問題データ（JSON）
├── manage.py
├── requirements.txt
├── .env.example             # 環境変数の設定例（自動読込はしない）
├── .gitignore               # Gitの追跡対象から除外するファイル
└── README.md
```

`db.sqlite3` は初回のマイグレーション時に作成されるローカルデータベースです。データベース、秘密情報、仮想環境、Pythonのキャッシュ、IDEの設定ファイルなどは `.gitignore` でGitの追跡対象から除外します。

## 動作環境

- Python 3.12 以上を推奨
- Django：`requirements.txt` に記載されたバージョン

## ローカル環境での起動方法

### 1. リポジトリを取得

```bash
git clone https://github.com/ryota29881/python-quiz-django
cd python-quiz-django
```

### 2. 仮想環境を作成

Windows PowerShellの場合：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. 必要なパッケージをインストール

```bash
python -m pip install -r requirements.txt
```

### 4. データベースを作成

```bash
python manage.py migrate
```

### 5. 問題データを登録

リポジトリには、4択問題とコード作成問題のJSONデータを含めています。

```bash
python manage.py import_questions
python manage.py import_code_questions
```

すでに登録済みの問題を削除してから再登録する場合は、以下を使用できます。

```bash
python manage.py import_questions --reset
python manage.py import_code_questions --reset
```

### 6. 開発サーバーを起動

```bash
python manage.py runserver
```

ブラウザで以下を開きます。

```text
http://127.0.0.1:8000/
```

## ユーザー登録・成績保存

ログインしなくてもクイズをプレイできます。

新規登録すると、ログイン後にクイズ結果がユーザーごとに保存されます。

マイページでは、以下を確認できます。

- 総プレイ回数
- 平均正答率
- 最高正答率
- 累計正解数
- 過去のクイズ履歴

## Django Admin

管理者アカウントを作成すると、Django Adminから問題を管理できます。

```bash
python manage.py createsuperuser
```

開発サーバー起動後、以下へアクセスします。

```text
http://127.0.0.1:8000/admin/
```

4択問題では、問題文や選択肢を管理できます。コード作成問題では、問題文・難易度・解説・判定用ルールなどを管理できます。

## テスト

以下のコマンドでテストを実行できます。

```bash
python manage.py test quiz code_quiz
```

## GitHubへ公開する際の注意

`.gitignore` では、以下をGitの追跡対象から除外します。

- `db.sqlite3` とデータベースの一時ファイル
- `.env` などの環境変数ファイル（`.env.example` は除く）
- 仮想環境（`venv/`、`.venv/`、`env/`）
- `__pycache__/`、`*.pyc` などのPythonキャッシュ・コンパイル済みファイル
- `.vscode/`、`.idea/` などのIDE設定
- OSが生成する一部のファイル

**注意：** `.gitignore` は、すでにGitで追跡されているファイルを自動で追跡解除するものではありません。公開済みのリポジトリでは、`git status` や `git ls-files` で追跡状態を確認してください。秘密情報がすでに公開されていた場合は、ファイルを削除するだけでなく、該当する秘密情報を変更してください。

### Djangoの秘密鍵・環境変数

Djangoの設定では、`DJANGO_SECRET_KEY` 環境変数が設定されていればその値を使用し、未設定の場合はローカル開発用の既定値を使用します。`DJANGO_DEBUG` と `DJANGO_ALLOWED_HOSTS` も環境変数から設定できます。

`.env.example` は設定値の記入例です。このプロジェクトは `.env` ファイルを自動読み込みしないため、ファイルを作成しただけでは環境変数は反映されません。ローカルで環境変数を設定する場合は、使用するシェルで設定するか、実行環境の環境変数設定を利用してください。

公開環境では、独自の強固な `DJANGO_SECRET_KEY` を設定し、`DJANGO_DEBUG=False` と適切な `DJANGO_ALLOWED_HOSTS` を指定してください。開発用の既定値を公開環境で使用しないでください。

## 制作目的

職業訓練校でPython・Tkinterを使用して制作したクイズアプリを、Djangoを使用してWebアプリ化しました。

Pythonの基礎知識をクイズ形式で確認できることに加え、Webアプリケーションとしての認証、データベース、管理画面、ユーザーごとの成績管理などを学習・実装することを目的としています。
