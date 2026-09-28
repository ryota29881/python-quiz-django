import random

from django.shortcuts import render, redirect

from .models import CodeQuestion
from .ast_judge import ASTJudge

from quiz.services import (
    calculate_accuracy,
    calculate_rank,
    save_quiz_history,
)


# ======================================================
# セッションキー
# ======================================================

SESSION_DIFFICULTY = "code_quiz_difficulty"
SESSION_QUESTION_ID = "code_quiz_question_id"
SESSION_QUESTION_IDS = "code_quiz_question_ids"
SESSION_QUESTION_INDEX = "code_quiz_question_index"
SESSION_SCORE = "code_quiz_score"
SESSION_ANSWERED = "code_quiz_answered"
SESSION_RESULT = "code_quiz_result"
SESSION_EXPLANATION = "code_quiz_explanation"
SESSION_HISTORY_SAVED = "code_quiz_history_saved"


# ======================================================
# 難易度選択
# ======================================================

def difficulty_select(request):

    reset_quiz_session(request)

    return render(
        request,
        "code_quiz/difficulty_select.html",
    )


# ======================================================
# クイズ終了
# ======================================================

def exit_quiz(request):

    reset_quiz_session(request)

    return redirect("home")


# ======================================================
# セッション初期化
# ======================================================

def reset_quiz_session(request):

    keys = [
        SESSION_DIFFICULTY,
        SESSION_QUESTION_ID,
        SESSION_QUESTION_IDS,
        SESSION_QUESTION_INDEX,
        SESSION_SCORE,
        SESSION_ANSWERED,
        SESSION_RESULT,
        SESSION_EXPLANATION,
        SESSION_HISTORY_SAVED,
    ]

    for key in keys:

        request.session.pop(
            key,
            None,
        )

    request.session.modified = True


# ======================================================
# クイズ開始
# ======================================================

def initialize_quiz(request, difficulty):

    questions = list(
        CodeQuestion.objects.filter(
            difficulty=difficulty
        )
    )

    if not questions:
        return []

    selected_questions = random.sample(
        questions,
        min(5, len(questions)),
    )

    question_ids = [
        question.id
        for question in selected_questions
    ]

    request.session[
        SESSION_DIFFICULTY
    ] = difficulty

    request.session[
        SESSION_QUESTION_IDS
    ] = question_ids

    request.session[
        SESSION_QUESTION_INDEX
    ] = 0

    request.session[
        SESSION_SCORE
    ] = 0

    request.session[
        SESSION_ANSWERED
    ] = False

    request.session[
        SESSION_RESULT
    ] = None

    request.session[
        SESSION_EXPLANATION
    ] = None

    request.session[
        SESSION_HISTORY_SAVED
    ] = False

    request.session.pop(
        SESSION_QUESTION_ID,
        None,
    )

    request.session.modified = True

    return question_ids


# ======================================================
# 履歴保存
# ======================================================

def save_history_if_needed(
    request,
    difficulty,
    score,
    total_questions,
):

    history_saved = request.session.get(
        SESSION_HISTORY_SAVED,
        False,
    )

    if history_saved:
        return

    if total_questions <= 0:
        return

    if not request.user.is_authenticated:
        return

    save_quiz_history(
        quiz_type="code",
        category="",
        difficulty=difficulty,
        score=score,
        total_questions=total_questions,
        user=request.user,
    )

    request.session[
        SESSION_HISTORY_SAVED
    ] = True

    request.session.modified = True


# ======================================================
# 結果画面
# ======================================================

def render_result(
    request,
    difficulty,
    score,
    total_questions,
):

    save_history_if_needed(
        request,
        difficulty,
        score,
        total_questions,
    )

    accuracy = calculate_accuracy(
        score,
        total_questions,
    )

    rank = calculate_rank(
        score,
        total_questions,
    )

    return render(
        request,
        "code_quiz/result.html",
        {
            "difficulty": difficulty,
            "score": score,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "rank": rank,
        },
    )


# ======================================================
# 問題表示
# ======================================================

def render_question(
    request,
    question,
    difficulty,
    question_index,
    total_questions,
):

    answered = request.session.get(
        SESSION_ANSWERED,
        False,
    )

    result = request.session.get(
        SESSION_RESULT,
    )

    explanation = request.session.get(
        SESSION_EXPLANATION,
    )

    score = request.session.get(
        SESSION_SCORE,
        0,
    )

    return render(
        request,
        "code_quiz/index.html",
        {
            "question": question,
            "difficulty": difficulty,
            "result": result,
            "explanation": explanation,
            "answered": answered,
            "question_number": question_index + 1,
            "total_questions": total_questions,
            "score": score,
        },
    )


# ======================================================
# メイン
# ======================================================

def index(request, difficulty):

    session_difficulty = request.session.get(
        SESSION_DIFFICULTY
    )

    # --------------------------------------------------
    # 難易度が変更された場合
    # --------------------------------------------------

    if session_difficulty != difficulty:

        reset_quiz_session(request)

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        # ==============================================
        # もう一度挑戦
        # ==============================================

        if action == "restart":

            reset_quiz_session(request)

            return redirect(
                "code_quiz",
                difficulty=difficulty,
            )

        # ==============================================
        # 結果を見る
        # ==============================================

        if action == "result":

            question_ids = request.session.get(
                SESSION_QUESTION_IDS,
                [],
            )

            score = request.session.get(
                SESSION_SCORE,
                0,
            )

            return render_result(
                request,
                difficulty,
                score,
                len(question_ids),
            )

        # ==============================================
        # 次の問題
        # ==============================================

        if action == "next":

            question_ids = request.session.get(
                SESSION_QUESTION_IDS,
                [],
            )

            question_index = request.session.get(
                SESSION_QUESTION_INDEX,
                0,
            )

            answered = request.session.get(
                SESSION_ANSWERED,
                False,
            )

            if not answered:

                return redirect(
                    "code_quiz",
                    difficulty=difficulty,
                )

            question_index += 1

            request.session[
                SESSION_QUESTION_INDEX
            ] = question_index

            request.session[
                SESSION_ANSWERED
            ] = False

            request.session[
                SESSION_RESULT
            ] = None

            request.session[
                SESSION_EXPLANATION
            ] = None

            request.session.pop(
                SESSION_QUESTION_ID,
                None,
            )

            request.session.modified = True

            if question_index >= len(question_ids):

                score = request.session.get(
                    SESSION_SCORE,
                    0,
                )

                return render_result(
                    request,
                    difficulty,
                    score,
                    len(question_ids),
                )

            return redirect(
                "code_quiz",
                difficulty=difficulty,
            )

        # ==============================================
        # 採点
        # ==============================================

        if action == "judge":

            question_id = request.session.get(
                SESSION_QUESTION_ID
            )

            question_ids = request.session.get(
                SESSION_QUESTION_IDS,
                [],
            )

            question_index = request.session.get(
                SESSION_QUESTION_INDEX,
                0,
            )

            score = request.session.get(
                SESSION_SCORE,
                0,
            )

            answered = request.session.get(
                SESSION_ANSWERED,
                False,
            )

            # ------------------------------------------
            # すでに回答済みの場合
            # ------------------------------------------

            if answered:

                if not question_id:

                    return redirect(
                        "code_quiz",
                        difficulty=difficulty,
                    )

                try:

                    question = CodeQuestion.objects.get(
                        id=question_id
                    )

                except CodeQuestion.DoesNotExist:

                    reset_quiz_session(request)

                    return redirect(
                        "code_quiz",
                        difficulty=difficulty,
                    )

                return render_question(
                    request,
                    question,
                    difficulty,
                    question_index,
                    len(question_ids),
                )

            # ------------------------------------------
            # 問題IDがない
            # ------------------------------------------

            if not question_id:

                return render(
                    request,
                    "code_quiz/index.html",
                    {
                        "question": None,
                        "difficulty": difficulty,
                        "result": "問題を取得できませんでした。",
                        "answered": False,
                    },
                )

            # ------------------------------------------
            # 問題取得
            # ------------------------------------------

            try:

                question = CodeQuestion.objects.get(
                    id=question_id
                )

            except CodeQuestion.DoesNotExist:

                request.session.pop(
                    SESSION_QUESTION_ID,
                    None,
                )

                return render(
                    request,
                    "code_quiz/index.html",
                    {
                        "question": None,
                        "difficulty": difficulty,
                        "result": "問題を取得できませんでした。",
                        "answered": False,
                    },
                )

            # ------------------------------------------
            # 入力コード
            # ------------------------------------------

            code = request.POST.get(
                "code",
                "",
            )

            # ------------------------------------------
            # AST採点
            # ------------------------------------------

            judge = ASTJudge()

            result = None
            explanation = None

            try:

                is_correct = judge.evaluate(
                    code,
                    question.rules,
                )

                if is_correct:

                    result = "正解！"

                    score += 1

                    request.session[
                        SESSION_SCORE
                    ] = score

                else:

                    result = "不正解"

                explanation = question.explanation

            except SyntaxError as error:

                result = "構文エラー"

                explanation = (
                    "Pythonコードの構文に問題があります。\n"
                    f"{error}"
                )

            # ------------------------------------------
            # 回答済みとして保存
            # ------------------------------------------

            request.session[
                SESSION_ANSWERED
            ] = True

            request.session[
                SESSION_RESULT
            ] = result

            request.session[
                SESSION_EXPLANATION
            ] = explanation

            request.session.modified = True

            # ------------------------------------------
            # ここでは結果画面へ移動しない
            #
            # 5問目でも一度、正解・不正解と
            # 解説を表示する
            # ------------------------------------------

            return render(
                request,
                "code_quiz/index.html",
                {
                    "question": question,
                    "difficulty": difficulty,
                    "result": result,
                    "explanation": explanation,
                    "answered": True,
                    "question_number": question_index + 1,
                    "total_questions": len(question_ids),
                    "score": score,
                },
            )

    # --------------------------------------------------
    # 問題セット取得
    # --------------------------------------------------

    question_ids = request.session.get(
        SESSION_QUESTION_IDS,
        [],
    )

    question_index = request.session.get(
        SESSION_QUESTION_INDEX,
        0,
    )

    score = request.session.get(
        SESSION_SCORE,
        0,
    )

    # --------------------------------------------------
    # 問題セットが存在しない
    # --------------------------------------------------

    if not question_ids:

        question_ids = initialize_quiz(
            request,
            difficulty,
        )

        if not question_ids:

            return render(
                request,
                "code_quiz/index.html",
                {
                    "question": None,
                    "difficulty": difficulty,
                    "result": "問題を取得できませんでした。",
                    "answered": False,
                },
            )

        question_index = 0
        score = 0

    # --------------------------------------------------
    # クイズ終了
    # --------------------------------------------------

    if question_index >= len(question_ids):

        return render_result(
            request,
            difficulty,
            score,
            len(question_ids),
        )

    # --------------------------------------------------
    # 現在の問題ID
    # --------------------------------------------------

    question_id = request.session.get(
        SESSION_QUESTION_ID
    )

    if not question_id:

        question_id = question_ids[
            question_index
        ]

        request.session[
            SESSION_QUESTION_ID
        ] = question_id

        request.session[
            SESSION_ANSWERED
        ] = False

        request.session[
            SESSION_RESULT
        ] = None

        request.session[
            SESSION_EXPLANATION
        ] = None

        request.session.modified = True

    # --------------------------------------------------
    # 問題取得
    # --------------------------------------------------

    try:

        question = CodeQuestion.objects.get(
            id=question_id
        )

    except CodeQuestion.DoesNotExist:

        request.session.pop(
            SESSION_QUESTION_ID,
            None,
        )

        return render(
            request,
            "code_quiz/index.html",
            {
                "question": None,
                "difficulty": difficulty,
                "result": "問題を取得できませんでした。",
                "answered": False,
            },
        )

    # --------------------------------------------------
    # 問題表示
    # --------------------------------------------------

    return render_question(
        request,
        question,
        difficulty,
        question_index,
        len(question_ids),
    )