from ast_judge import ASTJudge


judge = ASTJudge()


code = """
x = 10
print(x)
"""


rules = {
    "assignment": {
        "variable": "x",
        "value": 10
    },

    "print": {
        "variable": "x"
    }
}


result = judge.evaluate(
    code,
    rules
)


print(result)
