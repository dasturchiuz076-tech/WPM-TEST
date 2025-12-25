from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, Max, Sum
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Quiz, Question, QuizResult, QuizAttempt, UserQuizStat
from apps.history.models import Topic
from apps.users.models import UserActivity
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class QuizListView(ListView):
    model = Quiz
    template_name = 'testsystem/quiz_list.html'
    context_object_name = 'quizzes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Quiz.objects.filter(is_active=True).select_related('topic')
        
        # Filter by topic
        topic_slug = self.request.GET.get('topic')
        if topic_slug:
            queryset = queryset.filter(topic__slug=topic_slug)
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(topic__period__category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(topic__title__icontains=search_query)
            )
        
        # Check if user can take quiz (requirements met)
        if self.request.user.is_authenticated:
            user_completed_topics = set(self.request.user.progress_topics
                                       .filter(status='completed')
                                       .values_list('topic_id', flat=True))
            
            for quiz in queryset:
                required_ids = set(quiz.required_topics.values_list('id', flat=True))
                quiz.can_take = required_ids.issubset(user_completed_topics)
        else:
            for quiz in queryset:
                quiz.can_take = False
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.filter(is_active=True)[:20]
        context['difficulty_choices'] = Quiz.DIFFICULTY_CHOICES
        context['current_filters'] = {
            'topic': self.request.GET.get('topic'),
            'difficulty': self.request.GET.get('difficulty'),
            'category': self.request.GET.get('category'),
            'q': self.request.GET.get('q', ''),
        }
        return context


class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'testsystem/quiz_detail.html'
    context_object_name = 'quiz'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # Check if user can take this quiz
        can_take = False
        user_attempts = 0
        best_score = 0
        
        if self.request.user.is_authenticated:
            # Check requirements
            user_completed_topics = set(self.request.user.progress_topics
                                       .filter(status='completed')
                                       .values_list('topic_id', flat=True))
            required_ids = set(quiz.required_topics.values_list('id', flat=True))
            can_take = required_ids.issubset(user_completed_topics)
            
            # Get user attempts
            user_attempts = QuizResult.objects.filter(
                user=self.request.user,
                quiz=quiz
            ).count()
            
            # Get best score
            best_result = QuizResult.objects.filter(
                user=self.request.user,
                quiz=quiz
            ).order_by('-score').first()
            
            if best_result:
                best_score = best_result.score
        
        context.update({
            'can_take': can_take,
            'user_attempts': user_attempts,
            'best_score': best_score,
            'breadcrumbs': [
                {'title': 'Testlar', 'url': '/tests/'},
                {'title': quiz.title, 'url': quiz.get_absolute_url()},
            ]
        })
        return context


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check requirements
    user_completed_topics = set(request.user.progress_topics
                               .filter(status='completed')
                               .values_list('topic_id', flat=True))
    required_ids = set(quiz.required_topics.values_list('id', flat=True))
    
    if not required_ids.issubset(user_completed_topics):
        messages.error(request, 'Bu testni yechish uchun avval kerakli mavzularni o\'rganishingiz kerak!')
        return redirect('testsystem:quiz_detail', slug=quiz.slug)
    
    # Check max attempts
    user_attempts = QuizResult.objects.filter(
        user=request.user,
        quiz=quiz
    ).count()
    
    if user_attempts >= quiz.max_attempts:
        messages.error(request, f'Siz bu testni maksimal {quiz.max_attempts} marta yecha olasiz!')
        return redirect('testsystem:quiz_detail', slug=quiz.slug)
    
    # Create or resume attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz,
        is_completed=False,
        defaults={'current_question': quiz.questions.order_by('order').first()}
    )
    
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='quiz_take',
        object_type='quiz',
        object_id=quiz.id,
        description=f'"{quiz.title}" testini boshladi',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return redirect('testsystem:quiz_attempt', attempt_id=attempt.id)


class QuizAttemptView(LoginRequiredMixin, DetailView):
    model = QuizAttempt
    template_name = 'testsystem/quiz_attempt.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.get_object()
        
        if not attempt.current_question and not attempt.is_completed:
            # Get next question
            next_question = attempt.get_next_question()
            if next_question:
                attempt.current_question = next_question
                attempt.save()
        
        # Calculate time left
        time_limit_seconds = attempt.quiz.time_limit * 60
        time_elapsed = attempt.time_elapsed
        time_left = max(0, time_limit_seconds - time_elapsed)
        
        # Get answered questions count
        answered_count = len(attempt.answers)
        total_questions = attempt.quiz.question_count
        
        context.update({
            'time_left': time_left,
            'time_limit': attempt.quiz.time_limit,
            'answered_count': answered_count,
            'total_questions': total_questions,
            'progress_percentage': (answered_count / total_questions * 100) if total_questions > 0 else 0,
            'breadcrumbs': [
                {'title': 'Testlar', 'url': '/tests/'},
                {'title': attempt.quiz.title, 'url': attempt.quiz.get_absolute_url()},
                {'title': 'Testni yechish', 'url': ''},
            ]
        })
        return context
    
    def get(self, request, *args, **kwargs):
        attempt = self.get_object()
        
        if attempt.is_completed:
            messages.info(request, 'Bu test allaqachon tugatilgan!')
            return redirect('testsystem:result_detail', result_id=attempt.quiz.results
                          .filter(user=request.user).first().id)
        
        # Check time limit
        time_limit_seconds = attempt.quiz.time_limit * 60
        if attempt.time_elapsed > time_limit_seconds:
            # Auto-complete quiz if time is up
            result = attempt.calculate_score()
            attempt.is_completed = True
            attempt.completed_at = timezone.now()
            attempt.save()
            
            messages.warning(request, 'Vaqt tugadi! Test avtomatik ravishda yakunlandi.')
            return redirect('testsystem:result_detail', result_id=result.id)
        
        return super().get(request, *args, **kwargs)


@login_required
def submit_answer(request, attempt_id):
    if request.method == 'POST':
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        
        if attempt.is_completed:
            return JsonResponse({'error': 'Test allaqachon tugatilgan!'}, status=400)
        
        question_id = request.POST.get('question_id')
        answers = request.POST.getlist('answers[]')
        
        if not question_id:
            return JsonResponse({'error': 'Savol IDsi berilmadi!'}, status=400)
        
        # Save answers
        attempt.save_answers(question_id, answers)
        
        # Get next question
        next_question = attempt.get_next_question()
        
        if next_question:
            attempt.current_question = next_question
            attempt.save()
            
            return JsonResponse({
                'success': True,
                'next_question_id': next_question.id,
                'has_next': True
            })
        else:
            # No more questions, complete the quiz
            return JsonResponse({
                'success': True,
                'has_next': False,
                'redirect_url': reverse('testsystem:complete_quiz', args=[attempt.id])
            })
    
    return JsonResponse({'error': 'Faqat POST so\'rov qabul qilinadi!'}, status=400)


@login_required
def complete_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.is_completed:
        messages.info(request, 'Bu test allaqachon tugatilgan!')
        return redirect('testsystem:result_list')
    
    # Calculate score
    result = attempt.calculate_score()
    
    # Mark attempt as completed
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Update user stats
    user_stat, created = UserQuizStat.objects.get_or_create(
        user=request.user,
        quiz=attempt.quiz
    )
    user_stat.update_stats(result.score, result.time_taken)
    
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='quiz_complete',
        object_type='quiz',
        object_id=attempt.quiz.id,
        description=f'"{attempt.quiz.title}" testini {result.score}% bilan yakunladi',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(
        request, 
        f'Test muvaffaqiyatli yakunlandi! Sizning natijangiz: {result.score:.1f}%'
    )
    
    return redirect('testsystem:result_detail', result_id=result.id)


class QuizResultListView(LoginRequiredMixin, ListView):
    model = QuizResult
    template_name = 'testsystem/result_list.html'
    context_object_name = 'results'
    paginate_by = 15
    
    def get_queryset(self):
        return QuizResult.objects.filter(
            user=self.request.user
        ).select_related('quiz', 'quiz__topic').order_by('-completed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate overall stats
        stats = QuizResult.objects.filter(user=self.request.user).aggregate(
            total_quizzes=Count('id', distinct=True),
            passed_quizzes=Count('id', distinct=True, filter=Q(passed=True)),
            average_score=Avg('score'),
            total_time=Sum('time_taken')
        )
        
        context.update({
            'total_quizzes': stats['total_quizzes'] or 0,
            'passed_quizzes': stats['passed_quizzes'] or 0,
            'average_score': stats['average_score'] or 0,
            'total_time': stats['total_time'] or 0,
        })
        return context


class QuizResultDetailView(LoginRequiredMixin, DetailView):
    model = QuizResult
    template_name = 'testsystem/result_detail.html'
    context_object_name = 'result'
    pk_url_kwarg = 'result_id'
    
    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.get_object()
        
        # Get question details with user answers
        questions_data = []
        for question in result.quiz.questions.all().prefetch_related('answers'):
            user_answer_ids = result.answers_data.get(str(question.id), [])
            user_answers = question.answers.filter(id__in=user_answer_ids)
            correct_answers = question.correct_answers
            
            is_correct = set(user_answer_ids) == set(correct_answers.values_list('id', flat=True))
            
            questions_data.append({
                'question': question,
                'user_answers': user_answers,
                'correct_answers': correct_answers,
                'is_correct': is_correct,
                'points_earned': question.points if is_correct else 0,
            })
        
        context.update({
            'questions_data': questions_data,
            'breadcrumbs': [
                {'title': 'Natijalar', 'url': '/tests/results/'},
                {'title': f'{result.quiz.title} - {result.score}%', 'url': ''},
            ]
        })
        return context


class QuizLeaderboardView(ListView):
    template_name = 'testsystem/leaderboard.html'
    context_object_name = 'leaderboard'
    paginate_by = 20
    
    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        return QuizResult.objects.filter(
            quiz=quiz
        ).select_related('user').order_by('-score', 'time_taken')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        context.update({
            'quiz': quiz,
            'breadcrumbs': [
                {'title': 'Testlar', 'url': '/tests/'},
                {'title': quiz.title, 'url': quiz.get_absolute_url()},
                {'title': 'Reyting', 'url': ''},
            ]
        })
        return context


class OverallLeaderboardView(ListView):
    template_name = 'testsystem/overall_leaderboard.html'
    context_object_name = 'leaderboard'
    paginate_by = 50
    
    def get_queryset(self):
        # Get users with their average scores and quiz counts
        from django.db.models import Count, Avg
        
        return User.objects.filter(
            quiz_results__isnull=False
        ).annotate(
            quiz_count=Count('quiz_results', distinct=True),
            avg_score=Avg('quiz_results__score'),
            last_activity=Max('quiz_results__completed_at')
        ).order_by('-avg_score', '-quiz_count')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'title': 'Testlar', 'url': '/tests/'},
            {'title': 'Umumiy reyting', 'url': ''},
        ]
        return context


class PracticeView(LoginRequiredMixin, TemplateView):
    template_name = 'testsystem/practice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_404(Topic, id=topic_id)
        
        # Get questions from this topic's quizzes
        questions = Question.objects.filter(
            quiz__topic=topic,
            quiz__is_active=True
        ).select_related('quiz').prefetch_related('answers')[:50]
        
        context.update({
            'topic': topic,
            'questions': questions,
            'breadcrumbs': [
                {'title': 'Testlar', 'url': '/tests/'},
                {'title': topic.title, 'url': topic.get_absolute_url()},
                {'title': 'Mashq qilish', 'url': ''},
            ]
        })
        return context