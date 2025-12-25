from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .forms import LoginForm, RegisterForm, ProfileUpdateForm, CustomPasswordChangeForm
from .models import User, UserProfile, UserActivity, UserBookmark
from apps.history.models import Topic
from apps.testsystem.models import QuizResult
from django.db import models

class LoginView(CreateView):
    form_class = LoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description='Foydalanuvchi tizimga kirdi',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, f'Xush kelibsiz, {user.get_full_name() or user.username}!')
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class LogoutView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            description='Foydalanuvchi tizimdan chiqdi',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logout(request)
        messages.info(request, 'Siz tizimdan chiqdingiz.')
        return redirect('home')


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        user = form.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='register',
            description='Yangi foydalanuvchi ro\'yxatdan o\'tdi',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(
            self.request, 
            'Ro\'yxatdan o\'tish muvaffaqiyatli amalga oshirildi! '
            'Endi hisobingizga kiring.'
        )
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User statistics
        completed_quizzes = QuizResult.objects.filter(user=user).count()
        completed_topics = user.progress_topics.all().count()
        
        # Calculate study hours (mock data for now)
        study_hours = completed_topics * 1.5  # 1.5 hours per topic
        
        # Recent activities
        recent_activities = UserActivity.objects.filter(
            user=user
        ).select_related('user')[:10]
        
        # Average quiz score
        avg_score = QuizResult.objects.filter(user=user).aggregate(
            avg_score=models.Avg('score')
        )['avg_score'] or 0
        
        context.update({
            'completed_quizzes': completed_quizzes,
            'completed_topics': completed_topics,
            'study_hours': study_hours,
            'recent_activities': recent_activities,
            'average_score': round(avg_score, 1),
            'other_sessions': []  # Could implement session tracking
        })
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'profile'):
            context['profile_form'] = ProfileUpdateForm(
                instance=self.request.user.profile
            )
        return context
    
    def form_valid(self, form):
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='profile_update',
            description='Foydalanuvchi profilini yangiladi',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Profil muvaffaqiyatli yangilandi!')
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, UpdateView):
    form_class = CustomPasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='profile_update',
            description='Foydalanuvchi parolini o\'zgartirdi',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, 'Parol muvaffaqiyatli o\'zgartirildi!')
        return super().form_valid(form)


class BookmarkListView(LoginRequiredMixin, ListView):
    model = UserBookmark
    template_name = 'users/bookmarks.html'
    context_object_name = 'bookmarks'
    
    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user).select_related('topic')


@login_required
def add_bookmark(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    bookmark, created = UserBookmark.objects.get_or_create(
        user=request.user,
        topic=topic
    )
    
    if created:
        messages.success(request, f'"{topic.title}" mavzusi saqlandi!')
    else:
        messages.info(request, f'"{topic.title}" allaqachon saqlangan!')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_bookmark(request, topic_id):
    bookmark = get_object_or_404(
        UserBookmark, 
        user=request.user, 
        topic_id=topic_id
    )
    topic_title = bookmark.topic.title
    bookmark.delete()
    
    messages.success(request, f'"{topic_title}" mavzusi saqlanganlardan o\'chirildi!')
    return redirect(request.META.get('HTTP_REFERER', 'users:bookmarks'))


class UserActivityListView(LoginRequiredMixin, ListView):
    model = UserActivity
    template_name = 'users/activity.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        return UserActivity.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-created_at')