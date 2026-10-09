from django.contrib import admin

from .forms import CodeQuestionAdminForm
from .models import CodeQuestion


@admin.register(CodeQuestion)
class CodeQuestionAdmin(admin.ModelAdmin):

    form = CodeQuestionAdminForm

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
                )
            },
        ),
        (
            "使用するルール",
            {
                "fields": (
                    "rule_assignment",
                    "rule_print",
                    "rule_for_loop",
                    "rule_while_loop",
                    "rule_if_statement",
                    "rule_function",
                    "rule_class",
                    "rule_list_assignment",
                    "rule_dict_assignment",
                    "rule_compare",
                ),
                "description": "問題の採点に使用するルールをチェックしてください。チェックしたルールの設定項目が下に表示されます。",
            },
        ),
        (
            "ルール設定",
            {
                "fields": (
                    "assignment_variable",
                    "assignment_value",
                    "print_variable",
                    "for_use_range",
                    "for_target",
                    "for_print_variable",
                    "function_name",
                    "function_arg_count",
                    "function_has_return",
                    "class_name",
                    "list_variable",
                    "list_length",
                    "dict_variable",
                    "compare_operator",
                ),
            },
        ),
    )

    class Media:
        js = ("code_quiz/admin_rules.js",)
        css = {"all": ("code_quiz/admin_rules.css",)}

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
