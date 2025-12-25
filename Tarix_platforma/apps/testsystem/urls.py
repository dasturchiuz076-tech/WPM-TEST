from django.urls import path
from . import views

app_name = 'testsystem'

urlpatterns = [
    # Quiz list and detail
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('quiz/<slug:slug>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    
    # Quiz taking
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.QuizAttemptView.as_view(), name='quiz_attempt'),
    path('attempt/<int:attempt_id>/submit/', views.submit_answer, name='submit_answer'),
    path('attempt/<int:attempt_id>/complete/', views.complete_quiz, name='complete_quiz'),
    
    # Results
    path('results/', views.QuizResultListView.as_view(), name='result_list'),
    path('results/<int:result_id>/', views.QuizResultDetailView.as_view(), name='result_detail'),
    
    # Leaderboard
    path('leaderboard/<int:quiz_id>/', views.QuizLeaderboardView.as_view(), name='quiz_leaderboard'),
    path('leaderboard/', views.OverallLeaderboardView.as_view(), name='overall_leaderboard'),
    
    # Practice
    path('practice/<int:topic_id>/', views.PracticeView.as_view(), name='practice'),
]