from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class Quiz(models.Model):
    """Test (Quiz) modeli"""
    DIFFICULTY_CHOICES = [
        ('easy', _('Oson')),
        ('medium', _('O\'rta')),
        ('hard', _('Qiyin')),
        ('expert', _('Mutanosib')),
    ]
    
    title = models.CharField(_('sarlavha'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('tavsif'), blank=True)
    topic = models.ForeignKey('history.Topic', on_delete=models.CASCADE, 
                            related_name='quizzes', verbose_name=_('mavzu'))
    difficulty = models.CharField(_('murakkablik darajasi'), max_length=20, 
                                 choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.PositiveIntegerField(_('vaqt cheklovi (daqiqa)'), default=30)
    passing_score = models.PositiveIntegerField(_('o\'tish balli (%)'), default=70)
    max_attempts = models.PositiveIntegerField(_('maksimal urinishlar'), default=3)
    required_topics = models.ManyToManyField('history.Topic', 
                                           related_name='required_for_quizzes',
                                           blank=True, verbose_name=_('talab qilinadigan mavzular'))
    image = models.ImageField(_('rasm'), upload_to='quizzes/', blank=True, null=True)
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('test')
        verbose_name_plural = _('testlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['topic', 'difficulty']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('testsystem:quiz_detail', kwargs={'slug': self.slug})
    
    @property
    def question_count(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or 0


class Question(models.Model):
    """Test savollari"""
    QUESTION_TYPES = [
        ('single', _('Bitta to\'g\'ri javob')),
        ('multiple', _('Bir nechta to\'g\'ri javob')),
        ('true_false', _('To\'g\'ri/Noto\'g\'ri')),
        ('short_answer', _('Qisqa javob')),
        ('matching', _('Moslashtirish')),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, 
                           related_name='questions', verbose_name=_('test'))
    text = models.TextField(_('savol matni'))
    question_type = models.CharField(_('savol turi'), max_length=20, 
                                    choices=QUESTION_TYPES, default='single')
    explanation = models.TextField(_('izoh'), blank=True, 
                                  help_text=_('To\'g\'ri javobning tushuntirish'))
    image = models.ImageField(_('rasm'), upload_to='questions/', blank=True, null=True)
    points = models.PositiveIntegerField(_('ball'), default=1)
    order = models.PositiveIntegerField(_('tartib'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('savol')
        verbose_name_plural = _('savollar')
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['quiz', 'order']),
        ]
    
    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text
    
    @property
    def correct_answers(self):
        """To'g'ri javoblar ro'yxati"""
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """Savol javoblari"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, 
                               related_name='answers', verbose_name=_('savol'))
    text = models.TextField(_('javob matni'))
    is_correct = models.BooleanField(_('to\'g\'ri javob'), default=False)
    explanation = models.TextField(_('izoh'), blank=True, 
                                  help_text=_('Bu javobning tushuntirishi'))
    order = models.PositiveIntegerField(_('tartib'), default=0)
    
    class Meta:
        verbose_name = _('javob')
        verbose_name_plural = _('javoblar')
        ordering = ['order']
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]
    
    def __str__(self):
        return f"{self.text[:50]}... (To'g'ri: {self.is_correct})"


class QuizResult(models.Model):
    """Test natijalari"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='quiz_results', verbose_name=_('foydalanuvchi'))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, 
                           related_name='results', verbose_name=_('test'))
    score = models.FloatField(_('ball'), default=0)
    correct_answers = models.PositiveIntegerField(_('to\'g\'ri javoblar'), default=0)
    total_questions = models.PositiveIntegerField(_('jami savollar'), default=0)
    passed = models.BooleanField(_('o\'tdi'), default=False)
    time_taken = models.PositiveIntegerField(_('sarflangan vaqt (soniya)'), default=0)
    answers_data = models.JSONField(_('javoblar ma\'lumoti'), default=dict)
    completed_at = models.DateTimeField(_('tugatilgan vaqt'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('test natijasi')
        verbose_name_plural = _('test natijalari')
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['completed_at']),
        ]
        unique_together = ['user', 'quiz']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"
    
    @property
    def percentage(self):
        """Foizda natija"""
        if self.total_questions > 0:
            return (self.correct_answers / self.total_questions) * 100
        return 0
    
    @property
    def time_per_question(self):
        """Har bir savolga o'rtacha vaqt"""
        if self.total_questions > 0:
            return self.time_taken / self.total_questions
        return 0


class QuizAttempt(models.Model):
    """Test urinishlari (davom etayotgan testlar)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='quiz_attempts', verbose_name=_('foydalanuvchi'))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, 
                           related_name='attempts', verbose_name=_('test'))
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name=_('joriy savol'))
    answers = models.JSONField(_('javoblar'), default=dict)
    started_at = models.DateTimeField(_('boshlangan vaqt'), auto_now_add=True)
    completed_at = models.DateTimeField(_('tugatilgan vaqt'), null=True, blank=True)
    is_completed = models.BooleanField(_('tugatildi'), default=False)
    
    class Meta:
        verbose_name = _('test urinishi')
        verbose_name_plural = _('test urinishlari')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'quiz', 'is_completed']),
        ]
    
    def __str__(self):
        status = "Tugatilgan" if self.is_completed else "Davom etmoqda"
        return f"{self.user.username} - {self.quiz.title} - {status}"
    
    @property
    def time_elapsed(self):
        """O'tgan vaqt"""
        from django.utils import timezone
        if self.is_completed and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif not self.is_completed:
            return (timezone.now() - self.started_at).total_seconds()
        return 0
    
    def save_answers(self, question_id, answers):
        """Javoblarni saqlash"""
        if not self.answers:
            self.answers = {}
        
        self.answers[str(question_id)] = answers
        self.save()
    
    def get_next_question(self):
        """Keyingi savolni olish"""
        answered_questions = list(self.answers.keys())
        
        next_question = self.quiz.questions.exclude(
            id__in=answered_questions
        ).order_by('order').first()
        
        return next_question
    
    def calculate_score(self):
        """Natijani hisoblash"""
        if not self.is_completed:
            return None
        
        total_score = 0
        total_questions = self.quiz.questions.count()
        correct_answers = 0
        
        for question in self.quiz.questions.all():
            user_answers = self.answers.get(str(question.id), [])
            correct_answer_ids = list(question.correct_answers.values_list('id', flat=True))
            
            if question.question_type in ['single', 'multiple', 'true_false']:
                # Ko'p tanlov va to'g'ri/noto'g'ri savollar uchun
                if set(user_answers) == set(correct_answer_ids):
                    total_score += question.points
                    correct_answers += 1
        
        score_percentage = (total_score / self.quiz.total_points * 100) if self.quiz.total_points > 0 else 0
        
        # QuizResult yaratish yoki yangilash
        result, created = QuizResult.objects.get_or_create(
            user=self.user,
            quiz=self.quiz,
            defaults={
                'score': score_percentage,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'passed': score_percentage >= self.quiz.passing_score,
                'time_taken': int(self.time_elapsed),
                'answers_data': self.answers,
            }
        )
        
        if not created:
            result.score = score_percentage
            result.correct_answers = correct_answers
            result.total_questions = total_questions
            result.passed = score_percentage >= self.quiz.passing_score
            result.time_taken = int(self.time_elapsed)
            result.answers_data = self.answers
            result.save()
        
        return result


class UserQuizStat(models.Model):
    """Foydalanuvchi test statistikasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='quiz_stats', verbose_name=_('foydalanuvchi'))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, 
                           related_name='user_stats', verbose_name=_('test'))
    attempts_count = models.PositiveIntegerField(_('urinishlar soni'), default=0)
    best_score = models.FloatField(_('eng yaxshi ball'), default=0)
    average_score = models.FloatField(_('o\'rtacha ball'), default=0)
    total_time = models.PositiveIntegerField(_('umumiy vaqt (soniya)'), default=0)
    last_attempt = models.DateTimeField(_('so\'nggi urinish'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi test statistikasi')
        verbose_name_plural = _('foydalanuvchi test statistikasi')
        unique_together = ['user', 'quiz']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Best: {self.best_score}%"
    
    def update_stats(self, new_score, time_taken):
        """Statistikani yangilash"""
        self.attempts_count += 1
        self.best_score = max(self.best_score, new_score)
        
        # O'rtacha ballni yangilash
        if self.average_score == 0:
            self.average_score = new_score
        else:
            self.average_score = ((self.average_score * (self.attempts_count - 1)) + new_score) / self.attempts_count
        
        self.total_time += time_taken
        self.last_attempt = timezone.now()
        self.save()