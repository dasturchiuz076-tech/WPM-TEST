from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('topics/', views.TopicProgressView.as_view(), name='topic_progress'),
    path('quizzes/', views.QuizProgressView.as_view(), name='quiz_progress'),
    path('achievements/', views.AchievementListView.as_view(), name='achievements'),
    path('stats/', views.StatisticsView.as_view(), name='statistics'),
    path('learning-path/<int:category_id>/', views.LearningPathView.as_view(), name='learning_path'),
    path('update-progress/<int:topic_id>/', views.update_topic_progress, name='update_progress'),
]