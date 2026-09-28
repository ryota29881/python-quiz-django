from django.conf import settings
from django.db import models


class Question(models.Model):

    CATEGORY_CHOICES = [
        ("basic", "Python基礎"),
        ("cert", "Python3認定基礎試験対策"),
    ]

    DIFFICULTY_CHOICES = [
        ("easy", "初級"),
        ("normal", "中級"),
        ("hard", "上級"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
    )

    question = models.TextField()

    code = models.TextField(
        blank=True,
    )

    explanation = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.question


class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    text = models.CharField(
        max_length=500,
    )

    is_correct = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.text


class QuizHistory(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_histories",
    )

    QUIZ_TYPE_CHOICES = [
        ("select", "4択クイズ"),
        ("code", "コード作成クイズ"),
    ]

    DIFFICULTY_CHOICES = [
        ("easy", "初級"),
        ("normal", "中級"),
        ("hard", "上級"),
    ]

    RANK_CHOICES = [
        ("S", "S"),
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    quiz_type = models.CharField(
        max_length=20,
        choices=QUIZ_TYPE_CHOICES,
    )

    category = models.CharField(
        max_length=20,
        blank=True,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
    )

    score = models.PositiveIntegerField()

    total_questions = models.PositiveIntegerField()

    accuracy = models.FloatField()

    rank = models.CharField(
        max_length=1,
        choices=RANK_CHOICES,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.get_quiz_type_display()} "
            f"{self.score}/{self.total_questions}"
        )