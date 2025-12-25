from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTopicProgress(models.Model):
    """Foydalanuvchining mavzular bo'yicha progressi"""
    STATUS_CHOICES = [
        ('not_started', _('Boshlanmagan')),
        ('in_progress', _('Jarayonda')),
        ('completed', _('Yakunlangan')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='progress_topics', verbose_name=_('foydalanuvchi'))
    topic = models.ForeignKey('history.Topic', on_delete=models.CASCADE, 
                            related_name='user_progress', verbose_name=_('mavzu'))
    status = models.CharField(_('holati'), max_length=20, choices=STATUS_CHOICES, default='not_started')
    percentage = models.PositiveIntegerField(_('foiz'), default=0)
    notes = models.TextField(_('eslatmalar'), blank=True)
    last_accessed = models.DateTimeField(_('so\'nggi kirish'), auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi mavzu progressi')
        verbose_name_plural = _('foydalanuvchi mavzu progresslari')
        unique_together = ['user', 'topic']
        ordering = ['-last_accessed']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['last_accessed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.title} - {self.get_status_display()}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class UserLearningPath(models.Model):
    """Foydalanuvchi o'rganish yo'nalishi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='learning_paths', verbose_name=_('foydalanuvchi'))
    category = models.ForeignKey('history.Category', on_delete=models.CASCADE, 
                               related_name='learning_paths', verbose_name=_('kategoriya'))
    current_period = models.ForeignKey('history.Period', on_delete=models.SET_NULL, 
                                     null=True, blank=True, verbose_name=_('joriy davr'))
    current_topic = models.ForeignKey('history.Topic', on_delete=models.SET_NULL, 
                                    null=True, blank=True, verbose_name=_('joriy mavzu'))
    completed_periods = models.ManyToManyField('history.Period', 
                                             related_name='completed_by_users',
                                             blank=True, verbose_name=_('yakunlangan davrlar'))
    order_type = models.CharField(_('tartiblash turi'), max_length=20, 
                                 choices=[('chronological', _('Xronologik')), ('thematic', _('Tematik'))],
                                 default='chronological')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi o\'rganish yo\'nalishi')
        verbose_name_plural = _('foydalanuvchi o\'rganish yo\'nalishlari')
        unique_together = ['user', 'category']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
    
    def get_next_topic(self):
        """Keyingi mavzuni olish"""
        from apps.history.models import Topic
        
        if not self.current_period:
            # Start with earliest period
            first_period = self.category.periods.filter(is_active=True).order_by('start_year').first()
            if not first_period:
                return None
            self.current_period = first_period
            self.save()
        
        # Get next topic in current period
        next_topic = Topic.objects.filter(
            period=self.current_period,
            is_active=True,
            order__gt=self.current_topic.order if self.current_topic else 0
        ).order_by('order').first()
        
        if next_topic:
            return next_topic
        
        # Move to next period
        next_period = self.category.periods.filter(
            is_active=True,
            start_year__gt=self.current_period.start_year
        ).order_by('start_year').first()
        
        if next_period:
            self.current_period = next_period
            self.save()
            return next_period.topics.filter(is_active=True).order_by('order').first()
        
        return None


class Achievement(models.Model):
    """Yutuqlar"""
    ACHIEVEMENT_TYPES = [
        ('topic_completion', _('Mavzuni yakunlash')),
        ('quiz_performance', _('Test natijasi')),
        ('streak', _('Ketma-ketlik')),
        ('exploration', _('Tadqiqot')),
        ('speed', _('Tezlik')),
        ('mastery', _('Ustozlik')),
    ]
    
    title = models.CharField(_('sarlavha'), max_length=200)
    description = models.TextField(_('tavsif'))
    achievement_type = models.CharField(_('yutuq turi'), max_length=50, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(_('ikonka'), max_length=50, 
                           help_text=_('FontAwesome icon class nomi'))
    points = models.PositiveIntegerField(_('ball'), default=10)
    required_topics = models.ManyToManyField('history.Topic', 
                                           related_name='required_for_achievements',
                                           blank=True, verbose_name=_('talab qilinadigan mavzular'))
    required_quizzes = models.ManyToManyField('testsystem.Quiz', 
                                            related_name='required_for_achievements',
                                            blank=True, verbose_name=_('talab qilinadigan testlar'))
    required_score = models.PositiveIntegerField(_('talab qilinadigan ball (%)'), default=80, null=True, blank=True)
    required_streak = models.PositiveIntegerField(_('talab qilinadigan ketma-ketlik'), default=7, null=True, blank=True)
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('yutuq')
        verbose_name_plural = _('yutuqlar')
        ordering = ['achievement_type', 'points']
    
    def __str__(self):
        return self.title
    
    def check_requirements(self, user):
        """Foydalanuvchi yutuq talablariga javob berishini tekshirish"""
        if not self.is_active:
            return False
        
        # Check topic requirements
        if self.required_topics.exists():
            completed_topics = set(user.progress_topics
                                 .filter(status='completed')
                                 .values_list('topic_id', flat=True))
            required_ids = set(self.required_topics.values_list('id', flat=True))
            if not required_ids.issubset(completed_topics):
                return False
        
        # Check quiz requirements
        if self.required_quizzes.exists():
            for quiz in self.required_quizzes.all():
                result = quiz.results.filter(user=user, passed=True).first()
                if not result or result.score < (self.required_score or 0):
                    return False
        
        # Check streak requirement
        if self.required_streak:
            from datetime import timedelta
            from django.utils import timezone
            
            streak = 0
            today = timezone.now().date()
            
            for i in range(self.required_streak):
                check_date = today - timedelta(days=i)
                if user.activities.filter(
                    activity_type__in=['topic_view', 'quiz_complete'],
                    created_at__date=check_date
                ).exists():
                    streak += 1
                else:
                    break
            
            if streak < self.required_streak:
                return False
        
        return True


class UserAchievement(models.Model):
    """Foydalanuvchi yutuqlari"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='achievements', verbose_name=_('foydalanuvchi'))
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, 
                                  related_name='users', verbose_name=_('yutuq'))
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi yutug\'i')
        verbose_name_plural = _('foydalanuvchi yutuqlari')
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"