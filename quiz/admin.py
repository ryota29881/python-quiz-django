from django.contrib import admin

from .models import Choice, Question, QuizHistory


admin.site.site_header = "Pythonクイズアプリ 管理画面"
admin.site.site_title = "Pythonクイズアプリ 管理画面"
admin.site.index_title = "管理メニュー"


class ChoiceInline(admin.TabularInline):
    """4択問題の選択肢を、問題の編集画面で直接管理する。"""

    model = Choice
    fk_name = "question"
    extra = 0
    min_num = 0
    can_delete = True
    show_change_link = True

    fields = (
        "text",
        "is_correct",
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "category",
        "difficulty",
        "short_question",
        "choice_count",
        "created_at",
    )

    list_filter = (
        "category",
        "difficulty",
    )

    search_fields = (
        "question",
        "code",
        "explanation",
        "choices__text",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "問題情報",
            {
                "fields": (
                    "category",
                    "difficulty",
                    "question",
                    "code",
                    "explanation",
                )
            },
        ),
    )

    inlines = (ChoiceInline,)

    @admin.display(description="問題文")
    def short_question(self, obj):
        if len(obj.question) > 60:
            return obj.question[:60] + "..."
        return obj.question

    @admin.display(description="選択肢数")
    def choice_count(self, obj):
        return obj.choices.count()


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "question",
        "text",
        "is_correct",
    )

    list_filter = (
        "is_correct",
        "question__category",
        "question__difficulty",
    )

    search_fields = (
        "text",
        "question__question",
    )

    list_editable = (
        "is_correct",
    )

    ordering = (
        "question_id",
        "id",
    )


@admin.register(QuizHistory)
class QuizHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "quiz_type",
        "category_display",
        "difficulty",
        "score_display",
        "accuracy_display",
        "rank",
        "created_at",
    )

    list_filter = (
        "quiz_type",
        "category",
        "difficulty",
        "rank",
        "created_at",
    )

    search_fields = (
        "category",
        "user__username",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "user",
        "quiz_type",
        "category",
        "difficulty",
        "score",
        "total_questions",
        "accuracy",
        "rank",
        "created_at",
    )

    @admin.display(description="カテゴリ")
    def category_display(self, obj):
        if not obj.category:
            return "-"
        return dict(Question.CATEGORY_CHOICES).get(
            obj.category,
            obj.category,
        )

    @admin.display(description="得点")
    def score_display(self, obj):
        return f"{obj.score} / {obj.total_questions}"

    @admin.display(description="正答率")
    def accuracy_display(self, obj):
        return f"{obj.accuracy:.1f}%"
