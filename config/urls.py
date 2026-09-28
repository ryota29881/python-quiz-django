from django.contrib import admin
from django.urls import include, path
from quiz import views


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "accounts/",
        include("django.contrib.auth.urls")
    ),

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "quiz/",
        include("quiz.urls")
    ),

    path(
        "code-quiz/",
        include("code_quiz.urls")
    ),
]
