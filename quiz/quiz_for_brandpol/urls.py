from django.urls import path
from .views import HomeView, StartTestView, QuestionView, ResultView, AttemptHistoryView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tests/<int:test_id>/start/", StartTestView.as_view(), name="qfb_start"),
    path("attempts/<int:attempt_id>/questions/<int:question_id>/", QuestionView.as_view(), name="qfb_question"),
    path("attempts/<int:attempt_id>/result/", ResultView.as_view(), name="qfb_result"),
    path("attempts/history/", AttemptHistoryView.as_view(), name="qfb_history"),


    path("register/", views.register, name="register"),

    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("tests/<int:test_id>/start/", views.start_test, name="qfb_start"),
]
