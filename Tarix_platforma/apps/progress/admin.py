from django.contrib import admin
from .models import UserTopicProgress, UserLearningPath, Achievement, UserAchievement


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'status', 'percentage', 'last_accessed', 'created_at')
    list_filter = ('status', 'topic__period__category')
    search_fields = ('user__username', 'topic__title')
    list_editable = ('status', 'percentage')
    raw_id_fields = ('user', 'topic')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'topic')


@admin.register(UserLearningPath)
class UserLearningPathAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'current_period', 'completed_topics', 'total_topics', 'created_at')
    list_filter = ('category',)
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'current_period')
    
    def completed_topics(self, obj):
        return obj.user.progress_topics.filter(status='completed', topic__period__category=obj.category).count()
    
    def total_topics(self, obj):
        from apps.history.models import Topic
        return Topic.objects.filter(period__category=obj.category, is_active=True).count()


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'achievement_type', 'points', 'is_active')
    list_filter = ('achievement_type', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'points')
    filter_horizontal = ('required_topics',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement__achievement_type',)
    search_fields = ('user__username', 'achievement__title')
    readonly_fields = ('unlocked_at',)
    raw_id_fields = ('user', 'achievement')