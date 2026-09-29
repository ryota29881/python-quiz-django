# PYTHON LEARNING QUIZ

Python・Tkinterで制作したクイズアプリを、Djangoを使用したWebアプリケーションへ発展させたポートフォリオ作品です。

「Pythonの知識をクイズ形式で学ぶ」という元の作品の目的を維持しながら、Webアプリとして利用できるように、ユーザー認証・成績履歴・管理画面などを追加しています。

## 作品概要

- **4択クイズ**：カテゴリ・難易度を選択して5問出題
- **コード作成クイズ**：Pythonコードを入力して自動判定
- **解答・解説表示**：各問題の回答後に正誤と解説を表示
- **結果表示**：5問終了後にスコア・正答率・ランクを表示
- **ユーザー機能**：新規登録、ログイン、ログアウト
- **マイページ**：ログインユーザーの成績・クイズ履歴を表示
- **Django Admin**：問題、選択肢、コード問題、クイズ履歴を管理
- **レスポンシブ対応**：PC・スマートフォンの画面幅に対応
- **ASTによるコード判定**：コード作成クイズの入力内容をPythonのASTで解析

## 技術スタック

- Python
- Django 6.1.1
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
├── .env.example
├── .gitignore
└── README.md
```

※ `db.sqlite3`、仮想環境、PythonのキャッシュなどはGitHubへ公開しない構成にしています。

## 動作環境

- Python 3.12 以上を推奨
- Django 6.1.1

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
pip install -r requirements.txt
```

### 4. データベースを作成

```bash
python manage.py migrate
```

### 5. 問題データを登録

リポジトリには、4択問題90問とコード作成問題30問のJSONデータを含めています。

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

4択問題では、問題文と選択肢を同じ画面から管理できます。

コード作成問題では、問題文・難易度・解説・AST判定用ルールを管理できます。

## テスト

以下のコマンドでテストを実行できます。

```bash
python manage.py test quiz code_quiz
```

## GitHubへ公開する際の注意

このプロジェクトでは、以下をGitHubへ公開しないよう `.gitignore` を設定しています。

- `db.sqlite3`
- `.env`
- 仮想環境（`venv/` など）
- `__pycache__/`
- Pythonのコンパイル済みファイル
- IDEの設定ファイル

Djangoの`SECRET_KEY`もソースコードに固定値として記載せず、環境変数 `DJANGO_SECRET_KEY` から設定できるようにしています。

ローカル開発時は設定ファイルに用意した開発用の既定値が使用されます。公開環境では必ず独自の秘密鍵を環境変数に設定してください。

## 制作目的

職業訓練校でPython・Tkinterを使用して制作したクイズアプリを、Djangoを使用してWebアプリ化しました。

Pythonの基礎知識をクイズ形式で確認できることに加え、Webアプリケーションとしての認証、データベース、管理画面、ユーザーごとの成績管理などを学習・実装することを目的としています。
