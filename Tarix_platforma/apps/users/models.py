from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon raqami quyidagi formatda bo'lishi kerak: '+998901234567'. 9-15 ta raqam."
    )
    phone_number = models.CharField(_('telefon raqami'), validators=[phone_regex], max_length=17, blank=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi')
        verbose_name_plural = _('foydalanuvchilar')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_teacher(self):
        return self.groups.filter(name='Teachers').exists()


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', _('Erkak')),
        ('F', _('Ayol')),
        ('O', _('Boshqa')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(_('o\'zim haqimda'), max_length=500, blank=True)
    birth_date = models.DateField(_('tug\'ilgan sana'), null=True, blank=True)
    gender = models.CharField(_('jins'), max_length=1, choices=GENDER_CHOICES, blank=True)
    city = models.CharField(_('shahar'), max_length=100, blank=True)
    school = models.CharField(_('maktab/universitet'), max_length=200, blank=True)
    grade = models.CharField(_('sinf/kurs'), max_length=50, blank=True)
    interests = models.TextField(_('qiziqishlar'), blank=True)
    email_verified = models.BooleanField(_('email tasdiqlangan'), default=False)
    phone_verified = models.BooleanField(_('telefon tasdiqlangan'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi profili')
        verbose_name_plural = _('foydalanuvchi profillari')
    
    def __str__(self):
        return f"{self.user.username} profili"
    
    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', _('Kirish')),
        ('logout', _('Chiqish')),
        ('register', _('Ro\'yxatdan o\'tish')),
        ('profile_update', _('Profil yangilash')),
        ('topic_view', _('Mavzuni ko\'rish')),
        ('quiz_take', _('Test yechish')),
        ('quiz_complete', _('Test yakunlash')),
        ('progress_update', _('Progress yangilash')),
    ]
    
    OBJECT_TYPES = [
        ('user', _('Foydalanuvchi')),
        ('topic', _('Mavzu')),
        ('quiz', _('Test')),
        ('question', _('Savol')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(_('faollik turi'), max_length=50, choices=ACTIVITY_TYPES)
    object_type = models.CharField(_('obyekt turi'), max_length=50, choices=OBJECT_TYPES, blank=True)
    object_id = models.PositiveIntegerField(_('obyekt IDsi'), null=True, blank=True)
    description = models.TextField(_('tavsif'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP manzil'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('foydalanuvchi faolligi')
        verbose_name_plural = _('foydalanuvchi faolliklari')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"


class UserBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    topic = models.ForeignKey('history.Topic', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('belgilangan mavzu')
        verbose_name_plural = _('belgilangan mavzular')
        unique_together = ['user', 'topic']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.topic.title}"