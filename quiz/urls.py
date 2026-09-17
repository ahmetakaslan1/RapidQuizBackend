from django.urls import path
from .views import StartGameView, SubmitAnswerView, SubmitScoreView, GetCategoriesView, GetLeaderboardView

urlpatterns = [
    path('start-game/', StartGameView.as_view(), name='start-game'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('submit-score/', SubmitScoreView.as_view(), name='submit-score'),
    path('categories/', GetCategoriesView.as_view(), name='categories'),
    path('leaderboard/', GetLeaderboardView.as_view(), name='leaderboard'),
]
