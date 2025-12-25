from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
import random
import string

def generate_random_string(length=8):
    """Tasodifiy satr yaratish"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def calculate_estimated_time(text):
    """Matn o'qish uchun taxminiy vaqtni hisoblash"""
    # O'rtacha 200 so'z/daqiqa
    word_count = len(text.split())
    minutes = max(1, word_count // 200)
    return minutes

def format_time_ago(dt):
    """Vaqtni "necha vaqt oldin" formatida ko'rsatish"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} yil oldin"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} oy oldin"
    elif diff.days > 0:
        return f"{diff.days} kun oldin"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} soat oldin"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} daqiqa oldin"
    else:
        return "hozirgina"

def get_user_progress_summary(user):
    """Foydalanuvchi progressini umumlashtirish"""
    from apps.progress.models import UserTopicProgress
    from apps.testsystem.models import QuizResult
    
    topic_stats = UserTopicProgress.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed'))
    )
    
    quiz_stats = QuizResult.objects.filter(user=user).aggregate(
        total=Count('id'),
        passed=Count('id', filter=Q(passed=True))
    )
    
    return {
        'topics': {
            'total': topic_stats['total'] or 0,
            'completed': topic_stats['completed'] or 0,
            'percentage': (topic_stats['completed'] / topic_stats['total'] * 100) if topic_stats['total'] else 0
        },
        'quizzes': {
            'total': quiz_stats['total'] or 0,
            'passed': quiz_stats['passed'] or 0,
            'percentage': (quiz_stats['passed'] / quiz_stats['total'] * 100) if quiz_stats['total'] else 0
        }
    }