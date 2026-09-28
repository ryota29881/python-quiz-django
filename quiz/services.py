from .models import QuizHistory


def calculate_accuracy(score, total_questions):
    """
    正答率を計算する。

    例:
        5問中4問正解 → 80.0
    """

    if total_questions <= 0:
        return 0.0

    return (score / total_questions) * 100


def calculate_rank(score, total_questions):
    """
    正答率からランクを計算する。

    S : 100%
    A : 80%以上
    B : 60%以上
    C : 40%以上
    D : 40%未満
    """

    accuracy = calculate_accuracy(
        score,
        total_questions
    )

    if accuracy >= 100:
        return "S"

    if accuracy >= 80:
        return "A"

    if accuracy >= 60:
        return "B"

    if accuracy >= 40:
        return "C"

    return "D"


def save_quiz_history(
    quiz_type,
    category,
    difficulty,
    score,
    total_questions,
    user=None,
):
    """
    4択・コードクイズ共通の履歴保存処理。

    戻り値:
        作成した QuizHistory
    """

    accuracy = calculate_accuracy(
        score,
        total_questions
    )

    rank = calculate_rank(
        score,
        total_questions
    )

    return QuizHistory.objects.create(
        user=user,
        quiz_type=quiz_type,
        category=category,
        difficulty=difficulty,
        score=score,
        total_questions=total_questions,
        accuracy=accuracy,
        rank=rank,
    )