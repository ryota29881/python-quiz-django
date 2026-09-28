import json

from django.conf import settings
from django.core.management.base import BaseCommand

from quiz.models import Question, Choice


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
    help = "questions1.jsonから4択クイズをデータベースに登録します"

    def add_arguments(self, parser):

        parser.add_argument(
            "--reset",
            action="store_true",
            help="既存の4択クイズ問題を削除してから再登録します",
        )

    def handle(self, *args, **options):

        json_file = (
            settings.BASE_DIR
            / "question_data"
            / "questions1.json"
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

            question_count = Question.objects.count()

            Question.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"既存の4択問題を{question_count}件削除しました。"
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

            code = data.get(
                "code",
                "",
            ).strip()

            category = data.get(
                "category",
                "",
            )

            difficulty = data.get(
                "difficulty",
                "",
            )

            if not question_text:
                continue

            explanation = clean_explanation(
                data.get(
                    "explanation",
                    "",
                )
            )

            # --------------------------------------
            # 重複チェック
            # --------------------------------------

            exists = Question.objects.filter(
                category=category,
                difficulty=difficulty,
                question=question_text,
                code=code,
            ).exists()

            if exists:

                skipped_count += 1

                self.stdout.write(
                    f"スキップ: {question_text}"
                )

                continue

            # --------------------------------------
            # Question登録
            # --------------------------------------

            question = Question.objects.create(
                category=category,
                difficulty=difficulty,
                question=question_text,
                code=code,
                explanation=explanation,
            )

            # --------------------------------------
            # Choice登録
            # --------------------------------------

            choices = data.get(
                "choices",
                [],
            )

            answer_index = data.get(
                "answer_index"
            )

            for index, choice_text in enumerate(
                choices
            ):

                Choice.objects.create(
                    question=question,
                    text=str(choice_text),
                    is_correct=(
                        index == answer_index
                    ),
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
                "===== インポート完了 ====="
            )
        )

        self.stdout.write(
            f"追加件数: {added_count}"
        )

        self.stdout.write(
            f"スキップ件数: {skipped_count}"
        )