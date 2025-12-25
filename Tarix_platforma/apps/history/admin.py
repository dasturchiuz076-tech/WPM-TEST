from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Period, Topic, HistoricalFigure, Event, Document


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('title', 'slug', 'order', 'difficulty', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'start_year', 'end_year', 'order', 'topic_count', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('start_year',)
    
    inlines = [TopicInline]
    
    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Mavzular soni'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'order', 'difficulty', 'view_count', 'is_active', 'created_at')
    list_filter = ('period__category', 'period', 'difficulty', 'is_active')
    search_fields = ('title', 'content', 'summary')
    list_editable = ('order', 'difficulty', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'period', 'order', 'difficulty')
        }),
        ('Kontent', {
            'fields': ('content', 'summary', 'image')
        }),
        ('Statistika', {
            'fields': ('view_count', 'estimated_time', 'is_active')
        }),
        ('Sanamalar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistoricalFigure)
class HistoricalFigureAdmin(admin.ModelAdmin):
    list_display = ('name', 'lifespan', 'category', 'country', 'is_active')
    list_filter = ('category', 'country', 'is_active')
    search_fields = ('name', 'biography', 'achievements')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('related_topics',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'location', 'importance')
    list_filter = ('category', 'importance')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_topics', 'related_figures')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'year', 'document_type', 'is_verified')
    list_filter = ('category', 'document_type', 'is_verified')
    search_fields = ('title', 'content', 'description')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['file'].widget.attrs.update({'accept': '.pdf,.doc,.docx,.txt'})
        return form