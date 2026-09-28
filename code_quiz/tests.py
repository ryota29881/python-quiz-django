from django.test import TestCase
from django.urls import reverse

from .models import CodeQuestion


class CodeQuizTests(TestCase):

    def test_difficulty_select_is_available(self):
        response = self.client.get(
            reverse("code_quiz_difficulty_select")
        )

        self.assertEqual(response.status_code, 200)

    def test_question_can_be_started(self):
        CodeQuestion.objects.create(
            difficulty="easy",
            question="printする関数は？",
            explanation="print()を使います。",
            rules={
                "print": {
                    "variable": "x"
                }
            },
        )

        response = self.client.get(
            reverse(
                "code_quiz",
                kwargs={"difficulty": "easy"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "printする関数は？")
