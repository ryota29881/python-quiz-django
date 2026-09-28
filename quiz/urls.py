from django.urls import path
from . import views

urlpatterns = [

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "",
        views.category_select,
        name="index"
    ),

    path(
        "difficulty/<str:category>/",
        views.difficulty_select,
        name="difficulty_select"
    ),

    path(
        "start/<str:category>/<str:difficulty>/",
        views.start_quiz,
        name="start_quiz"
    ),

    path(
        "question/",
        views.question,
        name="question"
    ),

    path(
        "next/",
        views.next_question,
        name="next_question"
    ),

    path(
        "result/",
        views.result,
        name="result"
    ),

    path(
        "history/",
        views.history,
        name="history"
    ),
]