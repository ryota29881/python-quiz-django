import json

from django.conf import settings
from django.core.management.base import BaseCommand

from code_quiz.models import CodeQuestion


def clean_explanation(text):
    """
    解説に含まれる不要な行頭・行末の空白を削除する。
    """

    if not text:
        return ""

    lines = text.splitlines()

    cleaned_lines = [
        line.strip()
        for line in lines
    ]

    return "\n".join(
        cleaned_lines
    ).strip()


class Command(BaseCommand):

    help = "questions2.jsonからコード作成クイズをデータベースに登録します"

    def add_arguments(self, parser):

        parser.add_argument(
            "--reset",
            action="store_true",
            help="既存のコード作成クイズを削除してから再登録します",
        )

    def handle(self, *args, **options):

        json_file = (
            settings.BASE_DIR
            / "question_data"
            / "questions2.json"
        )

        if not json_file.exists():

            self.stdout.write(
                self.style.ERROR(
                    f"ファイルが見つかりません: {json_file}"
                )
            )

            return

        # ------------------------------------------
        # 既存問題の削除
        # ------------------------------------------

        if options["reset"]:

            question_count = (
                CodeQuestion.objects.count()
            )

            CodeQuestion.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"既存のコードクイズを{question_count}件削除しました。"
                )
            )

        # ------------------------------------------
        # JSON読み込み
        # ------------------------------------------

        with open(
            json_file,
            "r",
            encoding="utf-8",
        ) as f:

            questions = json.load(f)

        added_count = 0
        skipped_count = 0

        # ------------------------------------------
        # 問題登録
        # ------------------------------------------

        for data in questions:

            question_text = data.get(
                "question",
                "",
            ).strip()

            if not question_text:
                continue

            difficulty = data.get(
                "difficulty",
                "easy",
            )

            explanation = clean_explanation(
                data.get(
                    "explanation",
                    "",
                )
            )

            rules = data.get(
                "rules",
                {},
            )

            # --------------------------------------
            # 重複チェック
            # --------------------------------------

            exists = CodeQuestion.objects.filter(
                difficulty=difficulty,
                question=question_text,
            ).exists()

            if exists:

                skipped_count += 1

                self.stdout.write(
                    f"スキップ: {question_text}"
                )

                continue

            # --------------------------------------
            # 登録
            # --------------------------------------

            CodeQuestion.objects.create(

                difficulty=difficulty,

                question=question_text,

                explanation=explanation,

                rules=rules,

            )

            added_count += 1

            self.stdout.write(
                f"登録: {question_text}"
            )

        # ------------------------------------------
        # 結果表示
        # ------------------------------------------

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "===== コードクイズ インポート完了 ====="
            )
        )

        self.stdout.write(
            f"追加件数: {added_count}"
        )

        self.stdout.write(
            f"スキップ件数: {skipped_count}"
        )