import ast
import json

from django import forms

from .models import CodeQuestion


class CodeQuestionAdminForm(forms.ModelForm):
    """
    コード作成クイズの管理画面用フォーム。

    rules はJSONを直接入力させず、ルールのチェックボックスと
    各ルールに必要な設定項目からJSONを組み立てます。
    """

    RULE_CHOICES = (
        ("assignment", "変数への代入"),
        ("print", "print"),
        ("for_loop", "for文"),
        ("while_loop", "while文"),
        ("if_statement", "if文"),
        ("function", "関数定義"),
        ("class", "クラス定義"),
        ("list_assignment", "リスト"),
        ("dict_assignment", "辞書"),
        ("compare", "比較演算子"),
    )

    COMPARE_CHOICES = (
        ("Eq", "==（等しい）"),
        ("NotEq", "!=（等しくない）"),
        ("Gt", ">（より大きい）"),
        ("GtE", ">=（以上）"),
        ("Lt", "<（より小さい）"),
        ("LtE", "<=（以下）"),
    )

    rule_assignment = forms.BooleanField(
        label="変数への代入",
        required=False,
    )
    assignment_variable = forms.CharField(
        label="代入先の変数名",
        required=False,
        max_length=100,
        help_text="例: x = 10 の場合は x",
    )
    assignment_value = forms.CharField(
        label="代入する値",
        required=False,
        max_length=200,
        help_text='例: 10、3.14、"Hello"、True',
    )

    rule_print = forms.BooleanField(
        label="print",
        required=False,
    )
    print_variable = forms.CharField(
        label="printで出力する変数名",
        required=False,
        max_length=100,
    )

    rule_for_loop = forms.BooleanField(
        label="for文",
        required=False,
    )
    for_use_range = forms.BooleanField(
        label="rangeを使用",
        required=False,
    )
    for_target = forms.CharField(
        label="for文で使うループ変数名",
        required=False,
        max_length=100,
    )
    for_print_variable = forms.CharField(
        label="for文の中でprintする変数名",
        required=False,
        max_length=100,
    )

    rule_while_loop = forms.BooleanField(
        label="while文",
        required=False,
    )

    rule_if_statement = forms.BooleanField(
        label="if文",
        required=False,
    )

    rule_function = forms.BooleanField(
        label="関数定義",
        required=False,
    )
    function_name = forms.CharField(
        label="関数名",
        required=False,
        max_length=100,
    )
    function_arg_count = forms.IntegerField(
        label="引数の数",
        required=False,
        min_value=0,
    )
    function_has_return = forms.BooleanField(
        label="returnを使用",
        required=False,
    )

    rule_class = forms.BooleanField(
        label="クラス定義",
        required=False,
    )
    class_name = forms.CharField(
        label="クラス名",
        required=False,
        max_length=100,
    )

    rule_list_assignment = forms.BooleanField(
        label="リスト",
        required=False,
    )
    list_variable = forms.CharField(
        label="リストを代入する変数名",
        required=False,
        max_length=100,
        help_text="例: numbers = [1, 2, 3] の場合は numbers",
    )
    list_length = forms.IntegerField(
        label="要素数",
        required=False,
        min_value=0,
    )

    rule_dict_assignment = forms.BooleanField(
        label="辞書",
        required=False,
    )
    dict_variable = forms.CharField(
        label="辞書を代入する変数名",
        required=False,
        max_length=100,
        help_text="例: scores = {'A': 100} の場合は scores",
    )

    rule_compare = forms.BooleanField(
        label="比較演算子",
        required=False,
    )
    compare_operator = forms.ChoiceField(
        label="比較演算子",
        choices=COMPARE_CHOICES,
        required=False,
    )

    class Meta:
        model = CodeQuestion
        fields = (
            "difficulty",
            "question",
            "explanation",
        )
        widgets = {
            "question": forms.Textarea(attrs={"rows": 4}),
            "explanation": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rules = self.instance.rules if self.instance and self.instance.pk else {}
        if not isinstance(rules, dict):
            rules = {}

        self._existing_extra_rules = {
            key: value
            for key, value in rules.items()
            if key not in dict(self.RULE_CHOICES)
        }

        self._set_initial_from_rules(rules)

    def _set_initial_from_rules(self, rules):
        assignment = rules.get("assignment")
        if isinstance(assignment, dict):
            self.initial["rule_assignment"] = True
            self.initial["assignment_variable"] = assignment.get("variable", "")
            self.initial["assignment_value"] = self._value_to_text(
                assignment.get("value")
            )

        print_rule = rules.get("print")
        if isinstance(print_rule, dict):
            self.initial["rule_print"] = True
            self.initial["print_variable"] = print_rule.get("variable", "")

        for_rule = rules.get("for_loop")
        if isinstance(for_rule, dict):
            self.initial["rule_for_loop"] = True
            self.initial["for_use_range"] = bool(for_rule.get("use_range"))
            self.initial["for_target"] = for_rule.get("target", "")
            self.initial["for_print_variable"] = for_rule.get(
                "print_variable", ""
            )

        if "while_loop" in rules and isinstance(rules["while_loop"], dict):
            self.initial["rule_while_loop"] = True

        if "if_statement" in rules and isinstance(rules["if_statement"], dict):
            self.initial["rule_if_statement"] = True

        function = rules.get("function")
        if isinstance(function, dict):
            self.initial["rule_function"] = True
            self.initial["function_name"] = function.get("name", "")
            self.initial["function_arg_count"] = function.get("arg_count")
            self.initial["function_has_return"] = bool(function.get("has_return"))

        class_rule = rules.get("class")
        if isinstance(class_rule, dict):
            self.initial["rule_class"] = True
            self.initial["class_name"] = class_rule.get("name", "")

        list_rule = rules.get("list_assignment")
        if isinstance(list_rule, dict):
            self.initial["rule_list_assignment"] = True
            self.initial["list_variable"] = list_rule.get("variable", "")
            self.initial["list_length"] = self._to_int(list_rule.get("length"))

        dict_rule = rules.get("dict_assignment")
        if isinstance(dict_rule, dict):
            self.initial["rule_dict_assignment"] = True
            self.initial["dict_variable"] = dict_rule.get("variable", "")

        compare = rules.get("compare")
        if isinstance(compare, dict):
            self.initial["rule_compare"] = True
            self.initial["compare_operator"] = compare.get("operator", "")

    @staticmethod
    def _to_int(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _value_to_text(value):
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if value is True:
            return "True"
        if value is False:
            return "False"
        if value is None:
            return "None"
        return str(value)

    def clean(self):
        cleaned = super().clean()
        rules = dict(self._existing_extra_rules)

        if cleaned.get("rule_assignment"):
            variable = cleaned.get("assignment_variable", "").strip()
            value_text = cleaned.get("assignment_value", "").strip()
            if not variable:
                self.add_error("assignment_variable", "変数名を入力してください。")
            if not value_text:
                self.add_error("assignment_value", "代入する値を入力してください。")
            else:
                try:
                    value = ast.literal_eval(value_text)
                except (SyntaxError, ValueError):
                    value = value_text
                cleaned["_rule_assignment"] = {
                    "variable": variable,
                    "value": value,
                }

        if cleaned.get("rule_print"):
            variable = cleaned.get("print_variable", "").strip()
            if not variable:
                self.add_error("print_variable", "出力する変数名を入力してください。")
            cleaned["_rule_print"] = {"variable": variable}

        if cleaned.get("rule_for_loop"):
            rule = {}
            if cleaned.get("for_use_range"):
                rule["use_range"] = True
            target = cleaned.get("for_target", "").strip()
            print_variable = cleaned.get("for_print_variable", "").strip()
            if target:
                rule["target"] = target
            if print_variable:
                rule["print_variable"] = print_variable
            cleaned["_rule_for_loop"] = rule

        if cleaned.get("rule_while_loop"):
            cleaned["_rule_while_loop"] = {}

        if cleaned.get("rule_if_statement"):
            cleaned["_rule_if_statement"] = {}

        if cleaned.get("rule_function"):
            name = cleaned.get("function_name", "").strip()
            if not name:
                self.add_error("function_name", "関数名を入力してください。")
            arg_count = cleaned.get("function_arg_count")
            cleaned["_rule_function"] = {
                "name": name,
            }
            if arg_count is not None:
                cleaned["_rule_function"]["arg_count"] = arg_count
            if cleaned.get("function_has_return"):
                cleaned["_rule_function"]["has_return"] = True

        if cleaned.get("rule_class"):
            name = cleaned.get("class_name", "").strip()
            if not name:
                self.add_error("class_name", "クラス名を入力してください。")
            cleaned["_rule_class"] = {"name": name}

        if cleaned.get("rule_list_assignment"):
            variable = cleaned.get("list_variable", "").strip()
            if not variable:
                self.add_error("list_variable", "変数名を入力してください。")
            rule = {"variable": variable}
            if cleaned.get("list_length") is not None:
                rule["length"] = cleaned["list_length"]
            cleaned["_rule_list_assignment"] = rule

        if cleaned.get("rule_dict_assignment"):
            variable = cleaned.get("dict_variable", "").strip()
            if not variable:
                self.add_error("dict_variable", "変数名を入力してください。")
            cleaned["_rule_dict_assignment"] = {"variable": variable}

        if cleaned.get("rule_compare"):
            operator = cleaned.get("compare_operator")
            if not operator:
                self.add_error("compare_operator", "比較演算子を選択してください。")
            cleaned["_rule_compare"] = {"operator": operator}

        selected_rules = any(
            cleaned.get(f"rule_{rule_name}")
            for rule_name, _ in self.RULE_CHOICES
        )
        if not selected_rules:
            self.add_error(None, "少なくとも1つの採点ルールを選択してください。")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        rules = dict(self._existing_extra_rules)
        mappings = (
            ("assignment", "_rule_assignment"),
            ("print", "_rule_print"),
            ("for_loop", "_rule_for_loop"),
            ("while_loop", "_rule_while_loop"),
            ("if_statement", "_rule_if_statement"),
            ("function", "_rule_function"),
            ("class", "_rule_class"),
            ("list_assignment", "_rule_list_assignment"),
            ("dict_assignment", "_rule_dict_assignment"),
            ("compare", "_rule_compare"),
        )

        for rule_name, cleaned_name in mappings:
            if self.cleaned_data.get(f"rule_{rule_name}"):
                rules[rule_name] = self.cleaned_data.get(cleaned_name, {})
            else:
                rules.pop(rule_name, None)

        instance.rules = rules

        if commit:
            instance.save()
            self.save_m2m()
        return instance
