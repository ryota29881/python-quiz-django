from django.contrib import admin

from .models import CodeQuestion


@admin.register(CodeQuestion)
class CodeQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "difficulty",
        "short_question",
        "rule_count",
    )

    list_filter = (
        "difficulty",
    )

    search_fields = (
        "question",
        "explanation",
    )

    ordering = (
        "id",
    )

    fieldsets = (
        (
            "問題情報",
            {
                "fields": (
                    "difficulty",
                    "question",
                    "explanation",
                    "rules",
                )
            },
        ),
    )

    @admin.display(description="問題文")
    def short_question(self, obj):
        if len(obj.question) > 60:
            return obj.question[:60] + "..."
        return obj.question

    @admin.display(description="判定ルール数")
    def rule_count(self, obj):
        if isinstance(obj.rules, dict):
            return len(obj.rules)
        return 0
