from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q, Max
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import UserTopicProgress, UserLearningPath, Achievement, UserAchievement
from apps.history.models import Category, Period, Topic
from apps.testsystem.models import QuizResult, UserQuizStat
from apps.users.models import UserActivity


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Topic progress statistics
        topic_stats = UserTopicProgress.objects.filter(user=user).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            avg_percentage=Avg('percentage')
        )
        
        # Quiz statistics
        quiz_stats = QuizResult.objects.filter(user=user).aggregate(
            total_quizzes=Count('id', distinct=True),
            passed_quizzes=Count('id', distinct=True, filter=Q(passed=True)),
            avg_score=Avg('score'),
            total_time=Sum('time_taken')
        )
        
        # Recent activities
        recent_activities = UserActivity.objects.filter(
            user=user
        ).select_related('user').order_by('-created_at')[:10]
        
        # Learning paths
        learning_paths = UserLearningPath.objects.filter(user=user).select_related('category')
        
        # Achievements
        achievements = UserAchievement.objects.filter(
            user=user
        ).select_related('achievement').order_by('-unlocked_at')[:5]
        
        # Study streak
        streak = self.calculate_streak(user)
        
        # Weekly study time
        weekly_time = self.get_weekly_study_time(user)
        
        context.update({
            'topic_stats': topic_stats,
            'quiz_stats': quiz_stats,
            'recent_activities': recent_activities,
            'learning_paths': learning_paths,
            'achievements': achievements,
            'streak': streak,
            'weekly_time': weekly_time,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
            ]
        })
        return context
    
    def calculate_streak(self, user):
        """O'qish ketma-ketligini hisoblash"""
        streak = 0
        today = timezone.now().date()
        
        for i in range(365):  # Maksimal 1 yil
            check_date = today - timedelta(days=i)
            if user.activities.filter(
                activity_type__in=['topic_view', 'quiz_complete'],
                created_at__date=check_date
            ).exists():
                streak += 1
            else:
                break
        
        return streak
    
    def get_weekly_study_time(self, user):
        """Haftalik o'qish vaqtini hisoblash"""
        week_ago = timezone.now() - timedelta(days=7)
        
        # Topic view time (taxminiy: 5 daqiqa per view)
        topic_views = user.activities.filter(
            activity_type='topic_view',
            created_at__gte=week_ago
        ).count()
        topic_time = topic_views * 5 * 60  # 5 daqiqa * 60 soniya
        
        # Quiz time
        quiz_time = QuizResult.objects.filter(
            user=user,
            completed_at__gte=week_ago
        ).aggregate(total_time=Sum('time_taken'))['total_time'] or 0
        
        return topic_time + quiz_time


class TopicProgressView(LoginRequiredMixin, ListView):
    model = UserTopicProgress
    template_name = 'progress/topic_progress.html'
    context_object_name = 'progress_list'
    paginate_by = 20
    
    def get_queryset(self):
        return UserTopicProgress.objects.filter(
            user=self.request.user
        ).select_related('topic', 'topic__period', 'topic__period__category').order_by('-last_accessed')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Category-wise progress
        categories = Category.objects.filter(is_active=True).annotate(
            total_topics=Count('periods__topics', filter=Q(periods__topics__is_active=True)),
            completed_topics=Count('periods__topics', 
                                 filter=Q(periods__topics__user_progress__user=self.request.user,
                                         periods__topics__user_progress__status='completed'))
        )
        
        for category in categories:
            if category.total_topics > 0:
                category.progress_percentage = (category.completed_topics / category.total_topics) * 100
            else:
                category.progress_percentage = 0
        
        context.update({
            'categories': categories,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
                {'title': 'Mavzular progressi', 'url': ''},
            ]
        })
        return context


class QuizProgressView(LoginRequiredMixin, ListView):
    model = UserQuizStat
    template_name = 'progress/quiz_progress.html'
    context_object_name = 'quiz_stats'
    paginate_by = 20
    
    def get_queryset(self):
        return UserQuizStat.objects.filter(
            user=self.request.user
        ).select_related('quiz', 'quiz__topic').order_by('-last_attempt')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Difficulty-wise statistics
        difficulty_stats = QuizResult.objects.filter(
            user=self.request.user
        ).values('quiz__difficulty').annotate(
            count=Count('id'),
            avg_score=Avg('score'),
            best_score=Max('score')
        ).order_by('quiz__difficulty')
        
        context.update({
            'difficulty_stats': difficulty_stats,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
                {'title': 'Testlar progressi', 'url': ''},
            ]
        })
        return context


class AchievementListView(LoginRequiredMixin, ListView):
    model = Achievement
    template_name = 'progress/achievements.html'
    context_object_name = 'achievements'
    
    def get_queryset(self):
        achievements = Achievement.objects.filter(is_active=True)
        
        # Add unlocked status for each achievement
        user_achievements = set(
            self.request.user.achievements.values_list('achievement_id', flat=True)
        )
        
        for achievement in achievements:
            achievement.unlocked = achievement.id in user_achievements
            achievement.progress = self.calculate_achievement_progress(
                self.request.user, achievement
            )
        
        return achievements
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User's achievement statistics
        user_achievements = UserAchievement.objects.filter(
            user=self.request.user
        ).count()
        
        total_achievements = Achievement.objects.filter(is_active=True).count()
        
        context.update({
            'user_achievements': user_achievements,
            'total_achievements': total_achievements,
            'achievement_percentage': (user_achievements / total_achievements * 100) if total_achievements > 0 else 0,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
                {'title': 'Yutuqlar', 'url': ''},
            ]
        })
        return context
    
    def calculate_achievement_progress(self, user, achievement):
        """Yutuq progressini hisoblash"""
        progress = {'current': 0, 'total': 0, 'percentage': 0}
        
        if achievement.achievement_type == 'topic_completion':
            completed_topics = set(user.progress_topics
                                 .filter(status='completed')
                                 .values_list('topic_id', flat=True))
            required_ids = set(achievement.required_topics.values_list('id', flat=True))
            
            progress['current'] = len(completed_topics.intersection(required_ids))
            progress['total'] = len(required_ids)
        
        elif achievement.achievement_type == 'quiz_performance':
            passed_quizzes = 0
            for quiz in achievement.required_quizzes.all():
                result = quiz.results.filter(user=user, passed=True).first()
                if result and result.score >= (achievement.required_score or 0):
                    passed_quizzes += 1
            
            progress['current'] = passed_quizzes
            progress['total'] = achievement.required_quizzes.count()
        
        elif achievement.achievement_type == 'streak':
            from datetime import timedelta
            
            streak = 0
            today = timezone.now().date()
            
            for i in range(achievement.required_streak or 0):
                check_date = today - timedelta(days=i)
                if user.activities.filter(
                    activity_type__in=['topic_view', 'quiz_complete'],
                    created_at__date=check_date
                ).exists():
                    streak += 1
                else:
                    break
            
            progress['current'] = streak
            progress['total'] = achievement.required_streak or 0
        
        if progress['total'] > 0:
            progress['percentage'] = (progress['current'] / progress['total']) * 100
        
        return progress


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Daily study time for last 30 days
        daily_stats = []
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            
            # Topic views
            topic_views = user.activities.filter(
                activity_type='topic_view',
                created_at__date=date
            ).count()
            topic_time = topic_views * 5 * 60  # 5 minutes per view
            
            # Quiz time
            quiz_time = QuizResult.objects.filter(
                user=user,
                completed_at__date=date
            ).aggregate(total_time=Sum('time_taken'))['total_time'] or 0
            
            total_time = topic_time + quiz_time
            
            daily_stats.append({
                'date': date,
                'topic_views': topic_views,
                'quiz_time': quiz_time,
                'total_time': total_time
            })
        
        # Topic completion by category
        category_stats = []
        categories = Category.objects.filter(is_active=True)
        
        for category in categories:
            total_topics = Topic.objects.filter(
                period__category=category,
                is_active=True
            ).count()
            
            completed_topics = UserTopicProgress.objects.filter(
                user=user,
                topic__period__category=category,
                status='completed'
            ).count()
            
            if total_topics > 0:
                percentage = (completed_topics / total_topics) * 100
            else:
                percentage = 0
            
            category_stats.append({
                'category': category.name,
                'completed': completed_topics,
                'total': total_topics,
                'percentage': percentage
            })
        
        # Quiz performance by difficulty
        difficulty_stats = QuizResult.objects.filter(
            user=user
        ).values('quiz__difficulty').annotate(
            count=Count('id'),
            avg_score=Avg('score'),
            best_score=Max('score')
        ).order_by('quiz__difficulty')
        
        context.update({
            'daily_stats': daily_stats,
            'category_stats': category_stats,
            'difficulty_stats': difficulty_stats,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
                {'title': 'Statistika', 'url': ''},
            ]
        })
        return context


class LearningPathView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/learning_path.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category_id = self.kwargs.get('category_id')
        
        category = get_object_or_404(Category, id=category_id)
        
        # Get or create learning path
        learning_path, created = UserLearningPath.objects.get_or_create(
            user=user,
            category=category,
            defaults={'current_period': category.periods.order_by('start_year').first()}
        )
        
        # Get periods with progress
        periods = Period.objects.filter(
            category=category,
            is_active=True
        ).annotate(
            total_topics=Count('topics', filter=Q(topics__is_active=True)),
            completed_topics=Count('topics', 
                                 filter=Q(topics__user_progress__user=user,
                                         topics__user_progress__status='completed'))
        ).order_by('start_year')
        
        # Get next recommended topic
        next_topic = learning_path.get_next_topic()
        
        context.update({
            'category': category,
            'learning_path': learning_path,
            'periods': periods,
            'next_topic': next_topic,
            'breadcrumbs': [
                {'title': 'Progress', 'url': '/progress/'},
                {'title': category.name, 'url': ''},
                {'title': 'O\'rganish yo\'nalishi', 'url': ''},
            ]
        })
        return context


@login_required
def update_topic_progress(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        status = request.POST.get('status', 'in_progress')
        percentage = int(request.POST.get('percentage', 0))
        
        # Update or create progress
        progress, created = UserTopicProgress.objects.update_or_create(
            user=request.user,
            topic=topic,
            defaults={
                'status': status,
                'percentage': min(max(percentage, 0), 100)
            }
        )
        
        # Check for achievements
        check_achievements(request.user)
        
        messages.success(request, f'"{topic.title}" mavzusi progressi yangilandi!')
        
        if status == 'completed':
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='progress_update',
                object_type='topic',
                object_id=topic.id,
                description=f'"{topic.title}" mavzusini yakunladi',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return redirect(request.META.get('HTTP_REFERER', 'progress:dashboard'))
    
    return redirect('history:topic_detail', slug=topic.slug)


def check_achievements(user):
    """Foydalanuvchi yutuqlarini tekshirish"""
    achievements = Achievement.objects.filter(is_active=True)
    
    for achievement in achievements:
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            if achievement.check_requirements(user):
                UserAchievement.objects.create(user=user, achievement=achievement)