from django.contrib import admin
from .models import Quiz, Question, Answer, QuizResult, QuizAttempt


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ('text', 'is_correct', 'explanation', 'order')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'order')
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'question_count', 'time_limit', 
                   'passing_score', 'is_active', 'created_at')
    list_filter = ('difficulty', 'topic__period__category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'passing_score')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('required_topics',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'topic', 'description', 'image')
        }),
        ('Sozlamalar', {
            'fields': ('difficulty', 'time_limit', 'passing_score', 'max_attempts')
        }),
        ('Talablar', {
            'fields': ('required_topics', 'is_active')
        }),
        ('Sanamalar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Savollar soni'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz')
    search_fields = ('text',)
    list_editable = ('order', 'points')
    raw_id_fields = ('quiz',)
    
    inlines = [AnswerInline]
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Savol'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'explanation')
    list_editable = ('order', 'is_correct')
    raw_id_fields = ('question',)
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Javob'


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'time_taken', 'completed_at')
    list_filter = ('passed', 'quiz', 'completed_at')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('completed_at', 'time_taken', 'answers_data')
    date_hierarchy = 'completed_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'started_at', 'completed_at', 'is_completed')
    list_filter = ('is_completed', 'quiz')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at', 'current_question', 'answers')
    raw_id_fields = ('user', 'quiz')
    
    def has_add_permission(self, request):
        return False