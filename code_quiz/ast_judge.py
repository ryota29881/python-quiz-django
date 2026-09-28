import ast


class ASTJudge:
    """
    ユーザーが入力したPythonコードをASTで判定する。

    実際にコードを実行することはない。
    問題文で要求している構造をAST（抽象構文木）から確認する。
    """

    def evaluate(self, code, rules):
        """コードがすべてのルールを満たしている場合True。"""
        if not isinstance(code, str):
            return False
        if not isinstance(rules, dict):
            return False

        try:
            tree = ast.parse(code)
        except SyntaxError:
            raise

        # 採点条件が空の問題は「構文が正しいだけ」で正解にしない。
        if not rules:
            return False

        checks = [
            ("assignment", self.check_assignment),
            ("print", self.check_print),
            ("function", self.check_function),
            ("class", self.check_class),
            ("list_assignment", self.check_list_assignment),
            ("dict_assignment", self.check_dict_assignment),
            ("compare", self.check_compare),
        ]

        for rule_name, checker in checks:
            if rule_name not in rules:
                continue
            rule = rules[rule_name]
            if not isinstance(rule, dict):
                return False
            if not checker(tree, rule):
                return False

        if "for_loop" in rules:
            rule = rules["for_loop"]
            if rule is True:
                rule = {}
            if not isinstance(rule, dict):
                return False
            if not self.check_for_loop(tree, rule):
                return False

        if "while_loop" in rules:
            rule = rules["while_loop"]
            if rule is True:
                rule = {}
            if not isinstance(rule, dict):
                return False
            if not self.check_while_loop(tree, rule):
                return False

        if "if_statement" in rules:
            rule = rules["if_statement"]
            if rule is True:
                rule = {}
            if not isinstance(rule, dict):
                return False
            if not self.check_if_statement(tree, rule):
                return False

        return True

    def contains_variable(self, node, variable):
        """AST内に指定された変数名が存在するか。"""
        if not isinstance(variable, str):
            return False
        return any(
            isinstance(n, ast.Name) and n.id == variable
            for n in ast.walk(node)
        )

    def constant_matches(self, node, expected_value):
        """ASTの値とJSON側の期待値を比較する。"""
        return isinstance(node, ast.Constant) and node.value == expected_value

    def check_assignment(self, tree, rule):
        variable = rule.get("variable")
        expected_value = rule.get("value")
        if not isinstance(variable, str):
            return False

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == variable
                    and self.constant_matches(node.value, expected_value)
                ):
                    return True
        return False

    def check_print(self, tree, rule):
        """指定された変数をprintしているか。"""
        variable = rule.get("variable")
        if not isinstance(variable, str):
            return False

        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                continue
            if any(self.contains_variable(arg, variable) for arg in node.args):
                return True
        return False

    def get_for_loops(self, tree):
        return [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.For)
        ]

    def check_for_loop(self, tree, rule):
        """for文の存在と、指定があればrange・変数・print等を確認する。"""
        loops = self.get_for_loops(tree)
        if not loops:
            return False

        if rule.get("use_range"):
            if not any(self.is_range_call(loop.iter) for loop in loops):
                return False

        target = rule.get("target")
        if target:
            if not any(self.loop_target_is(loop.target, target) for loop in loops):
                return False

        print_variable = rule.get("print_variable")
        if print_variable:
            if not any(
                self.body_contains_print(loop.body, print_variable)
                for loop in loops
            ):
                return False

        return True

    def is_range_call(self, node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "range"
        )

    def loop_target_is(self, target, name):
        if isinstance(target, ast.Name):
            return target.id == name
        if isinstance(target, (ast.Tuple, ast.List)):
            return any(self.loop_target_is(element, name) for element in target.elts)
        return False

    def body_contains_print(self, body, variable):
        for statement in body:
            for node in ast.walk(statement):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "print"
                    and any(
                        self.contains_variable(arg, variable)
                        for arg in node.args
                    )
                ):
                    return True
        return False

    def check_while_loop(self, tree, rule):
        loops = [node for node in ast.walk(tree) if isinstance(node, ast.While)]
        if not loops:
            return False
        return True

    def check_if_statement(self, tree, rule):
        if_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.If)]
        if not if_nodes:
            return False
        return True

    def check_compare(self, tree, rule):
        operator_name = rule.get("operator")
        if not isinstance(operator_name, str):
            return False

        operator_class = getattr(ast, operator_name, None)
        if operator_class is None:
            return False

        return any(
            isinstance(node, ast.Compare)
            and any(isinstance(op, operator_class) for op in node.ops)
            for node in ast.walk(tree)
        )

    def check_function(self, tree, rule):
        name = rule.get("name")
        if not isinstance(name, str):
            return False

        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ]
        if not functions:
            return False

        arg_count = rule.get("arg_count")
        if arg_count is not None:
            try:
                expected = int(arg_count)
            except (TypeError, ValueError):
                return False
            if not any(self.function_arg_count(function) == expected for function in functions):
                return False

        if rule.get("has_return"):
            if not any(self.function_has_return(function) for function in functions):
                return False

        return True

    def function_arg_count(self, function):
        args = function.args
        positional = list(args.posonlyargs) + list(args.args)
        return len(positional)

    def function_has_return(self, function):
        return any(isinstance(node, ast.Return) for node in ast.walk(function))

    def get_function(self, tree, name):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return node
        return None

    def check_class(self, tree, rule):
        name = rule.get("name")
        if not isinstance(name, str):
            return False
        return any(
            isinstance(node, ast.ClassDef) and node.name == name
            for node in ast.walk(tree)
        )

    def check_list_assignment(self, tree, rule):
        variable = rule.get("variable")
        if not isinstance(variable, str):
            return False

        expected_length = rule.get("length")

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            target_matches = any(
                isinstance(target, ast.Name) and target.id == variable
                for target in node.targets
            )
            if not target_matches or not isinstance(node.value, ast.List):
                continue

            if expected_length is None:
                return True
            try:
                if len(node.value.elts) == int(expected_length):
                    return True
            except (TypeError, ValueError):
                return False

        return False

    def check_dict_assignment(self, tree, rule):
        variable = rule.get("variable")
        if not isinstance(variable, str):
            return False

        return any(
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == variable
                for target in node.targets
            )
            and isinstance(node.value, ast.Dict)
            for node in ast.walk(tree)
        )
