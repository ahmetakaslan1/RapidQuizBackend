from django.urls import path
from .views import StartGameView, SubmitAnswerView, SubmitScoreView

urlpatterns = [
    path('start-game/', StartGameView.as_view(), name='start-game'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('submit-score/', SubmitScoreView.as_view(), name='submit-score'),
]
