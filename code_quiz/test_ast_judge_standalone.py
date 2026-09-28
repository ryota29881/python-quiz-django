import json
from pathlib import Path

from ast_judge import ASTJudge


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "question_data" / "questions2.json"


def load_questions():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def main():
    questions = load_questions()
    judge = ASTJudge()

    assert len(questions) == 30

    # 以前「a」でも正解になっていたfor文問題。
    assert judge.evaluate("a", questions[3]["rules"]) is False
    assert judge.evaluate("for i in range(3):\n    print(i)", questions[3]["rules"]) is True

    # for + range
    assert judge.evaluate("for i in range(3):\n    pass", questions[11]["rules"]) is True
    assert judge.evaluate("for i in [1, 2, 3]:\n    pass", questions[11]["rules"]) is False

    # if + comparison
    assert judge.evaluate("if x > 0:\n    print(x)", questions[13]["rules"]) is True
    assert judge.evaluate("if x == 0:\n    print(x)", questions[13]["rules"]) is False

    # for + i + print(i)
    assert judge.evaluate("for i in range(3):\n    print(i)", questions[18]["rules"]) is True
    assert judge.evaluate("for j in range(3):\n    print(j)", questions[18]["rules"]) is False

    # list length + for
    assert judge.evaluate("numbers = [1, 2, 3, 4, 5]\nfor n in numbers:\n    print(n)", questions[25]["rules"]) is True
    assert judge.evaluate("numbers = [1, 2]\nfor n in numbers:\n    print(n)", questions[25]["rules"]) is False

    # while + if
    assert judge.evaluate("while x < 5:\n    if x > 0:\n        x += 1", questions[27]["rules"]) is True
    assert judge.evaluate("while x < 5:\n    x += 1", questions[27]["rules"]) is False

    # function argument count + return + for/range
    assert judge.evaluate(
        "def count_up(n):\n    for i in range(n):\n        print(i)\n    return n",
        questions[28]["rules"],
    ) is True
    assert judge.evaluate(
        "def count_up():\n    for i in range(3):\n        print(i)\n    return 3",
        questions[28]["rules"],
    ) is False

    # Empty rules must never accept arbitrary syntactically valid code.
    assert judge.evaluate("print('hello')", {}) is False

    print("AST judge standalone tests: PASS")


if __name__ == "__main__":
    main()
