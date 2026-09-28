import random

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)

from .models import Question, QuizHistory
from .services import (
    calculate_accuracy,
    calculate_rank,
    save_quiz_history,
)


def register(request):
    """
    ユーザー登録画面
    """

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("home")

    else:

        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        },
    )


@require_POST
def logout_view(request):
    """
    ログアウト処理
    """

    logout(request)

    return redirect("home")


def home(request):
    """
    アプリ全体のタイトル画面
    """

    return render(
        request,
        "quiz/home.html",
    )


def category_select(request):
    """
    クイズカテゴリ選択画面
    """

    categories = Question.CATEGORY_CHOICES

    return render(
        request,
        "quiz/category_select.html",
        {
            "categories": categories,
        },
    )


def difficulty_select(request, category):
    """
    難易度選択画面
    """

    difficulties = Question.DIFFICULTY_CHOICES

    category_display = dict(
        Question.CATEGORY_CHOICES
    ).get(
        category,
        category,
    )

    return render(
        request,
        "quiz/difficulty_select.html",
        {
            "category": category,
            "category_display": category_display,
            "difficulties": difficulties,
        },
    )


def start_quiz(request, category, difficulty):
    """
    クイズ開始処理
    """

    questions = list(
        Question.objects.filter(
            category=category,
            difficulty=difficulty,
        )
    )

    if not questions:
        category_display = dict(
            Question.CATEGORY_CHOICES
        ).get(
            category,
            category,
        )

        difficulty_display = dict(
            Question.DIFFICULTY_CHOICES
        ).get(
            difficulty,
            difficulty,
        )

        return render(
            request,
            "quiz/difficulty_select.html",
            {
                "category": category,
                "category_display": category_display,
                "difficulties": Question.DIFFICULTY_CHOICES,
                "error_message": (
                    f"{category_display}・{difficulty_display}の問題がありません。"
                    "管理画面または問題データを確認してください。"
                ),
            },
            status=404,
        )

    selected_questions = random.sample(
        questions,
        min(5, len(questions)),
    )

    request.session["quiz_questions"] = [
        question.id
        for question in selected_questions
    ]

    request.session["current_index"] = 0
    request.session["score"] = 0

    request.session["quiz_category"] = category
    request.session["quiz_difficulty"] = difficulty

    request.session["quiz_answered"] = False
    request.session["quiz_history_saved"] = False

    request.session.modified = True

    return redirect("question")


def question(request):
    """
    クイズ問題画面
    """

    quiz_questions = request.session.get(
        "quiz_questions",
        [],
    )

    current_index = request.session.get(
        "current_index",
        0,
    )

    score = request.session.get(
        "score",
        0,
    )

    category = request.session.get(
        "quiz_category",
        "",
    )

    difficulty = request.session.get(
        "quiz_difficulty",
        "",
    )

    answered = request.session.get(
        "quiz_answered",
        False,
    )

    # クイズが開始されていない場合
    if not quiz_questions:
        return redirect("index")

    # すべての問題が終了している場合
    if current_index >= len(quiz_questions):
        return redirect("result")

    question_id = quiz_questions[current_index]

    question = get_object_or_404(
        Question,
        id=question_id,
    )

    result_text = None
    explanation = None

    # 正解の選択肢
    correct_choice = question.choices.filter(
        is_correct=True
    ).first()

    # ------------------------------------------
    # 回答処理
    # ------------------------------------------

    if request.method == "POST" and not answered:

        choice_id = request.POST.get(
            "choice"
        )

        if not choice_id:

            result_text = "回答を選択してください。"

        else:

            try:

                selected_choice = question.choices.get(
                    id=choice_id
                )

            except question.choices.model.DoesNotExist:

                result_text = "不正な回答です。"

            else:

                answered = True

                request.session[
                    "quiz_answered"
                ] = True

                if selected_choice.is_correct:

                    result_text = "正解！"

                    score += 1

                    request.session[
                        "score"
                    ] = score

                else:

                    result_text = "不正解"

                explanation = question.explanation

                request.session.modified = True

    elif answered:

        result_text = request.session.get(
            "quiz_result"
        )

        explanation = question.explanation

    # ------------------------------------------
    # 結果をセッションにも保存
    # ------------------------------------------

    if answered and result_text:

        request.session[
            "quiz_result"
        ] = result_text

        request.session.modified = True

    # 表示用カテゴリ名
    category_display = dict(
        Question.CATEGORY_CHOICES
    ).get(
        category,
        category,
    )

    # 表示用難易度名
    difficulty_display = dict(
        Question.DIFFICULTY_CHOICES
    ).get(
        difficulty,
        difficulty,
    )

    return render(
        request,
        "quiz/index.html",
        {
            "question": question,
            "result": result_text,
            "explanation": explanation,
            "correct_choice": correct_choice,
            "answered": answered,
            "current_index": current_index + 1,
            "total_questions": len(quiz_questions),
            "category": category_display,
            "difficulty": difficulty_display,
            "score": score,
        },
    )


def next_question(request):
    """
    次の問題へ進む
    """

    current_index = request.session.get(
        "current_index",
        0,
    )

    quiz_questions = request.session.get(
        "quiz_questions",
        [],
    )

    request.session[
        "quiz_answered"
    ] = False

    request.session.pop(
        "quiz_result",
        None,
    )

    current_index += 1

    request.session[
        "current_index"
    ] = current_index

    request.session.modified = True

    if current_index >= len(quiz_questions):
        return redirect("result")

    return redirect("question")


def result(request):
    """
    結果画面
    """

    score = request.session.get(
        "score",
        0,
    )

    total_questions = len(
        request.session.get(
            "quiz_questions",
            [],
        )
    )

    accuracy = calculate_accuracy(
        score,
        total_questions,
    )

    rank = calculate_rank(
        score,
        total_questions,
    )

    category = request.session.get(
        "quiz_category",
        "",
    )

    difficulty = request.session.get(
        "quiz_difficulty",
        "",
    )

    category_display = dict(
        Question.CATEGORY_CHOICES
    ).get(
        category,
        category,
    )

    difficulty_display = dict(
        Question.DIFFICULTY_CHOICES
    ).get(
        difficulty,
        difficulty,
    )

    # ------------------------------------------
    # 履歴保存
    # ------------------------------------------

    history_saved = request.session.get(
        "quiz_history_saved",
        False,
    )

    if (
        not history_saved
        and total_questions > 0
        and request.user.is_authenticated
    ):

        save_quiz_history(
            quiz_type="select",
            category=category,
            difficulty=difficulty,
            score=score,
            total_questions=total_questions,
            user=request.user,
        )

        request.session[
            "quiz_history_saved"
        ] = True

        request.session.modified = True

    return render(
        request,
        "quiz/result.html",
        {
            "score": score,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "rank": rank,
            "category": category,
            "difficulty": difficulty,
            "category_display": category_display,
            "difficulty_display": difficulty_display,
        },
    )


@login_required
def history(request):
    """
    ログインユーザー専用のクイズ履歴・成績統計画面
    """

    histories = list(
        QuizHistory.objects.filter(
            user=request.user
        ).order_by(
            "-created_at"
        )
    )

    total_play_count = len(
        histories
    )

    total_score = sum(
        history.score
        for history in histories
    )

    total_questions = sum(
        history.total_questions
        for history in histories
    )

    if total_play_count > 0:

        average_accuracy = sum(
            history.accuracy
            for history in histories
        ) / total_play_count

        highest_accuracy = max(
            history.accuracy
            for history in histories
        )

    else:

        average_accuracy = 0
        highest_accuracy = 0

    # ------------------------------------------
    # クイズ種別ごとの成績
    # ------------------------------------------

    quiz_type_stats = []

    for quiz_type, quiz_type_display in QuizHistory.QUIZ_TYPE_CHOICES:

        type_histories = [
            history
            for history in histories
            if history.quiz_type == quiz_type
        ]

        if type_histories:

            type_play_count = len(type_histories)

            type_average_accuracy = sum(
                history.accuracy
                for history in type_histories
            ) / type_play_count

            type_highest_accuracy = max(
                history.accuracy
                for history in type_histories
            )

            type_score = sum(
                history.score
                for history in type_histories
            )

            type_questions = sum(
                history.total_questions
                for history in type_histories
            )

        else:

            type_play_count = 0
            type_average_accuracy = 0
            type_highest_accuracy = 0
            type_score = 0
            type_questions = 0

        quiz_type_stats.append(
            {
                "label": quiz_type_display,
                "play_count": type_play_count,
                "average_accuracy": type_average_accuracy,
                "highest_accuracy": type_highest_accuracy,
                "score": type_score,
                "questions": type_questions,
            }
        )

    # ------------------------------------------
    # 4択クイズのカテゴリごとの成績
    # ------------------------------------------

    category_stats = []

    for category, category_display in Question.CATEGORY_CHOICES:

        category_histories = [
            history
            for history in histories
            if (
                history.quiz_type == "select"
                and history.category == category
            )
        ]

        if category_histories:

            category_play_count = len(category_histories)

            category_average_accuracy = sum(
                history.accuracy
                for history in category_histories
            ) / category_play_count

            category_highest_accuracy = max(
                history.accuracy
                for history in category_histories
            )

        else:

            category_play_count = 0
            category_average_accuracy = 0
            category_highest_accuracy = 0

        category_stats.append(
            {
                "label": category_display,
                "play_count": category_play_count,
                "average_accuracy": category_average_accuracy,
                "highest_accuracy": category_highest_accuracy,
            }
        )

    return render(
        request,
        "quiz/history.html",
        {
            "histories": histories,
            "total_play_count": total_play_count,
            "total_score": total_score,
            "total_questions": total_questions,
            "average_accuracy": average_accuracy,
            "highest_accuracy": highest_accuracy,
            "quiz_type_stats": quiz_type_stats,
            "category_stats": category_stats,
        },
    )

