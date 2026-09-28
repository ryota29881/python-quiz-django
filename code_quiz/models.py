from django.db import models


class CodeQuestion(models.Model):

    DIFFICULTY_CHOICES = [
        ("easy", "初級"),
        ("normal", "中級"),
        ("hard", "上級"),
    ]

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
    )

    question = models.TextField()

    explanation = models.TextField()

    rules = models.JSONField()

    def __str__(self):
        return self.question
