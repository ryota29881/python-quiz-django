from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import QuizHistory
from .services import save_quiz_history


User = get_user_model()


class AuthenticationTests(TestCase):

    def test_register_logs_user_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )


class QuizHistoryTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="StrongPass123!",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="StrongPass123!",
        )

        save_quiz_history(
            quiz_type="select",
            category="basic",
            difficulty="easy",
            score=4,
            total_questions=5,
            user=self.user1,
        )

        save_quiz_history(
            quiz_type="code",
            category="",
            difficulty="normal",
            score=5,
            total_questions=5,
            user=self.user2,
        )

    def test_history_requires_login(self):
        response = self.client.get(reverse("history"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('history')}",
        )

    def test_history_only_shows_current_users_records(self):
        self.client.login(
            username="user1",
            password="StrongPass123!",
        )

        response = self.client.get(reverse("history"))

        self.assertEqual(response.status_code, 200)
        histories = response.context["histories"]
        self.assertEqual(len(histories), 1)
        self.assertEqual(histories[0].user, self.user1)
        self.assertEqual(histories[0].score, 4)


    def test_history_provides_dashboard_statistics(self):
        self.client.login(
            username="user1",
            password="StrongPass123!",
        )

        response = self.client.get(reverse("history"))

        self.assertEqual(response.status_code, 200)

        quiz_type_stats = response.context["quiz_type_stats"]
        self.assertEqual(len(quiz_type_stats), 2)
        self.assertEqual(quiz_type_stats[0]["play_count"], 1)
        self.assertEqual(quiz_type_stats[0]["average_accuracy"], 80.0)

        category_stats = response.context["category_stats"]
        self.assertEqual(len(category_stats), 2)
        self.assertEqual(category_stats[0]["play_count"], 1)
        self.assertEqual(category_stats[0]["average_accuracy"], 80.0)

        self.assertContains(response, "クイズ種別ごとの成績")
        self.assertContains(response, "4択クイズ・カテゴリ別成績")
        self.assertContains(response, "Rank A")

    def test_history_page_is_available_for_logged_in_user(self):
        self.client.login(
            username="user1",
            password="StrongPass123!",
        )

        response = self.client.get(reverse("history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user1")
        self.assertContains(response, "Python基礎")


class QuizServiceTests(TestCase):

    def test_save_quiz_history_keeps_user(self):
        user = User.objects.create_user(
            username="serviceuser",
            password="StrongPass123!",
        )

        history = save_quiz_history(
            quiz_type="select",
            category="basic",
            difficulty="easy",
            score=3,
            total_questions=5,
            user=user,
        )

        self.assertEqual(history.user, user)
        self.assertEqual(history.accuracy, 60.0)
        self.assertEqual(history.rank, "B")
