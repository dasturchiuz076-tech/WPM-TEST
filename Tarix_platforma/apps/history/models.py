from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """Tarix kategoriyalari: Jahon tarixi, O'zbekiston tarixi"""
    name = models.CharField(_('nomi'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('tavsif'))
    icon = models.CharField(_('ikonka'), max_length=50, blank=True, 
                           help_text=_('FontAwesome icon class nomi'))
    color = models.CharField(_('rang'), max_length=7, default='#3498db')
    order = models.PositiveIntegerField(_('tartib'), default=0)
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('kategoriya')
        verbose_name_plural = _('kategoriyalar')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('history:category_detail', kwargs={'slug': self.slug})


class Period(models.Model):
    """Tarixiy davrlar"""
    name = models.CharField(_('nomi'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='periods', verbose_name=_('kategoriya'))
    description = models.TextField(_('tavsif'))
    start_year = models.IntegerField(_('boshlanish yili'))
    end_year = models.IntegerField(_('tugash yili'))
    image = models.ImageField(_('rasm'), upload_to='periods/', blank=True, null=True)
    order = models.PositiveIntegerField(_('tartib'), default=0)
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('davr')
        verbose_name_plural = _('davrlar')
        ordering = ['start_year']
        unique_together = ['category', 'slug']
    
    def __str__(self):
        return f"{self.name} ({self.start_year}-{self.end_year})"
    
    def get_absolute_url(self):
        return reverse('history:period_detail', kwargs={'slug': self.slug})
    
    @property
    def century(self):
        """Davr asrini hisoblash"""
        return f"{self.start_year//100 + 1}-asr"


class Topic(models.Model):
    """Tarixiy mavzular"""
    DIFFICULTY_CHOICES = [
        ('beginner', _('Boshlang\'ich')),
        ('intermediate', _('O\'rta')),
        ('advanced', _('Murakkab')),
    ]
    
    title = models.CharField(_('sarlavha'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, 
                             related_name='topics', verbose_name=_('davr'))
    content = models.TextField(_('kontent'))
    summary = models.TextField(_('qisqacha mazmuni'), blank=True)
    image = models.ImageField(_('rasm'), upload_to='topics/', blank=True, null=True)
    difficulty = models.CharField(_('murakkablik darajasi'), max_length=20, 
                                 choices=DIFFICULTY_CHOICES, default='intermediate')
    order = models.PositiveIntegerField(_('tartib'), default=0)
    view_count = models.PositiveIntegerField(_('ko\'rishlar soni'), default=0)
    estimated_time = models.PositiveIntegerField(_('taxminiy vaqt (daqiqa)'), default=30)
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('mavzu')
        verbose_name_plural = _('mavzular')
        ordering = ['period__start_year', 'order', 'title']
        indexes = [
            models.Index(fields=['period', 'difficulty']),
            models.Index(fields=['view_count']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('history:topic_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class HistoricalFigure(models.Model):
    """Tarixiy shaxslar"""
    name = models.CharField(_('ism'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    biography = models.TextField(_('tarjimai holi'))
    achievements = models.TextField(_('yutuqlari'))
    birth_year = models.IntegerField(_('tug\'ilgan yili'), blank=True, null=True)
    death_year = models.IntegerField(_('vafot yili'), blank=True, null=True)
    image = models.ImageField(_('rasm'), upload_to='figures/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='figures', verbose_name=_('kategoriya'))
    country = models.CharField(_('mamlakati'), max_length=100, blank=True)
    related_topics = models.ManyToManyField(Topic, related_name='figures', 
                                          blank=True, verbose_name=_('bog\'liq mavzular'))
    is_active = models.BooleanField(_('faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('tarixiy shaxs')
        verbose_name_plural = _('tarixiy shaxslar')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def lifespan(self):
        if self.birth_year and self.death_year:
            return f"{self.birth_year}-{self.death_year}"
        elif self.birth_year:
            return f"{self.birth_year}-"
        return 'Noma\'lum'


class Event(models.Model):
    """Tarixiy voqealar"""
    IMPORTANCE_CHOICES = [
        ('low', _('Past')),
        ('medium', _('O\'rta')),
        ('high', _('Yuqori')),
        ('critical', _('Muhim')),
    ]
    
    title = models.CharField(_('sarlavha'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('tavsif'))
    date = models.DateField(_('sana'))
    location = models.CharField(_('joy'), max_length=200, blank=True)
    image = models.ImageField(_('rasm'), upload_to='events/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='events', verbose_name=_('kategoriya'))
    importance = models.CharField(_('ahamiyati'), max_length=20, 
                                 choices=IMPORTANCE_CHOICES, default='medium')
    related_topics = models.ManyToManyField(Topic, related_name='events', 
                                          blank=True, verbose_name=_('bog\'liq mavzular'))
    related_figures = models.ManyToManyField(HistoricalFigure, related_name='events', 
                                           blank=True, verbose_name=_('bog\'liq shaxslar'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('tarixiy voqea')
        verbose_name_plural = _('tarixiy voqealar')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} ({self.date})"


class Document(models.Model):
    """Tarixiy hujjatlar"""
    DOCUMENT_TYPES = [
        ('book', _('Kitob')),
        ('article', _('Maqola')),
        ('letter', _('Xat')),
        ('treaty', _('Shartnoma')),
        ('decree', _('Farmon')),
        ('other', _('Boshqa')),
    ]
    
    title = models.CharField(_('sarlavha'), max_length=200)
    description = models.TextField(_('tavsif'))
    content = models.TextField(_('mazmuni'), blank=True)
    year = models.IntegerField(_('yili'))
    author = models.CharField(_('muallif'), max_length=200, blank=True)
    document_type = models.CharField(_('hujjat turi'), max_length=20, 
                                    choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(_('fayl'), upload_to='documents/', blank=True, null=True)
    image = models.ImageField(_('rasm'), upload_to='documents/images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='documents', verbose_name=_('kategoriya'))
    is_verified = models.BooleanField(_('tasdiqlangan'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('tarixiy hujjat')
        verbose_name_plural = _('tarixiy hujjatlar')
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.title} ({self.year})"