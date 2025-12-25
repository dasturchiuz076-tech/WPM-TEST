from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    # Categories
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Periods
    path('periods/', views.PeriodListView.as_view(), name='period_list'),
    path('period/<slug:slug>/', views.PeriodDetailView.as_view(), name='period_detail'),
    
    # Topics
    path('topics/', views.TopicListView.as_view(), name='topic_list'),
    path('topic/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('topic/<int:pk>/read/', views.mark_topic_as_read, name='mark_topic_read'),
    
    # Historical figures
    path('figures/', views.HistoricalFigureListView.as_view(), name='figure_list'),
    path('figure/<slug:slug>/', views.HistoricalFigureDetailView.as_view(), name='figure_detail'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('event/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Documents
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    
    # Search
    path('search/', views.HistorySearchView.as_view(), name='search'),
]