from django.urls import path

from . import views


urlpatterns = [

    # コードクイズの難易度選択
    path(
        "",
        views.difficulty_select,
        name="code_quiz_difficulty_select",
    ),

    # コードクイズ終了
    path(
        "exit/",
        views.exit_quiz,
        name="code_quiz_exit",
    ),

    # コードクイズ
    path(
        "<str:difficulty>/",
        views.index,
        name="code_quiz",
    ),
]