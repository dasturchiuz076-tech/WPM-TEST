from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Category, Period, Topic, HistoricalFigure, Event, Document
from apps.users.models import UserActivity


class CategoryListView(ListView):
    model = Category
    template_name = 'history/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).annotate(
            period_count=Count('periods', distinct=True),
            topic_count=Count('periods__topics', distinct=True)
        )


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'history/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get periods for this category
        periods = Period.objects.filter(
            category=category, 
            is_active=True
        ).annotate(
            topic_count=Count('topics')
        ).order_by('start_year')
        
        # Get featured topics
        featured_topics = Topic.objects.filter(
            period__category=category,
            is_active=True
        ).order_by('-view_count')[:5]
        
        context.update({
            'periods': periods,
            'featured_topics': featured_topics,
            'breadcrumbs': [
                {'title': 'Kategoriyalar', 'url': '/history/'},
                {'title': category.name, 'url': category.get_absolute_url()},
            ]
        })
        return context


class PeriodListView(ListView):
    model = Period
    template_name = 'history/period_list.html'
    context_object_name = 'periods'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Period.objects.filter(is_active=True).select_related('category')
        
        # Filter by category if specified
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.annotate(topic_count=Count('topics')).order_by('start_year')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PeriodDetailView(DetailView):
    model = Period
    template_name = 'history/period_detail.html'
    context_object_name = 'period'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.get_object()
        
        # Get topics for this period
        topics = period.topics.filter(is_active=True).order_by('order', 'title')
        
        # Get related figures and events
        figures = HistoricalFigure.objects.filter(
            related_topics__period=period
        ).distinct()[:10]
        
        events = Event.objects.filter(
            related_topics__period=period
        ).order_by('-date')[:10]
        
        context.update({
            'topics': topics,
            'figures': figures,
            'events': events,
            'breadcrumbs': [
                {'title': 'Davrlar', 'url': '/history/periods/'},
                {'title': period.name, 'url': period.get_absolute_url()},
            ]
        })
        return context
    
    def get(self, request, *args, **kwargs):
        # Log activity if user is authenticated
        if request.user.is_authenticated:
            period = self.get_object()
            UserActivity.objects.create(
                user=request.user,
                activity_type='topic_view',
                object_type='period',
                object_id=period.id,
                description=f'{period.name} davrini ko\'rish',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return super().get(request, *args, **kwargs)


class TopicListView(ListView):
    model = Topic
    template_name = 'history/topic_list.html'
    context_object_name = 'topics'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Topic.objects.filter(
            is_active=True
        ).select_related('period', 'period__category')
        
        # Filters
        period_slug = self.request.GET.get('period')
        if period_slug:
            queryset = queryset.filter(period__slug=period_slug)
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(period__category__slug=category_slug)
        
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        # Ordering
        ordering = self.request.GET.get('ordering', 'order')
        if ordering in ['order', 'title', '-view_count', '-created_at']:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periods'] = Period.objects.filter(is_active=True)[:10]
        context['categories'] = Category.objects.filter(is_active=True)
        context['difficulty_choices'] = Topic.DIFFICULTY_CHOICES
        context['current_filters'] = {
            'period': self.request.GET.get('period'),
            'category': self.request.GET.get('category'),
            'difficulty': self.request.GET.get('difficulty'),
            'q': self.request.GET.get('q', ''),
            'ordering': self.request.GET.get('ordering', 'order'),
        }
        return context


class TopicDetailView(DetailView):
    model = Topic
    template_name = 'history/topic_detail.html'
    context_object_name = 'topic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        
        # Increment view count
        topic.increment_view_count()
        
        # Get related figures and events
        figures = topic.figures.all()[:10]
        events = topic.events.all()[:10]
        
        # Get next and previous topics
        next_topic = Topic.objects.filter(
            period=topic.period,
            order__gt=topic.order,
            is_active=True
        ).order_by('order').first()
        
        prev_topic = Topic.objects.filter(
            period=topic.period,
            order__lt=topic.order,
            is_active=True
        ).order_by('-order').first()
        
        # Check if user has bookmarked this topic
        is_bookmarked = False
        if self.request.user.is_authenticated:
            is_bookmarked = self.request.user.bookmarks.filter(topic=topic).exists()
        
        context.update({
            'figures': figures,
            'events': events,
            'next_topic': next_topic,
            'prev_topic': prev_topic,
            'is_bookmarked': is_bookmarked,
            'breadcrumbs': [
                {'title': 'Mavzular', 'url': '/history/topics/'},
                {'title': topic.period.name, 'url': topic.period.get_absolute_url()},
                {'title': topic.title, 'url': topic.get_absolute_url()},
            ]
        })
        return context
    
    def get(self, request, *args, **kwargs):
        # Log activity if user is authenticated
        if request.user.is_authenticated:
            topic = self.get_object()
            UserActivity.objects.create(
                user=request.user,
                activity_type='topic_view',
                object_type='topic',
                object_id=topic.id,
                description=f'"{topic.title}" mavzusini o\'qish',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return super().get(request, *args, **kwargs)


@LoginRequiredMixin
def mark_topic_as_read(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    
    # Create or update user progress
    from apps.progress.models import UserTopicProgress
    progress, created = UserTopicProgress.objects.get_or_create(
        user=request.user,
        topic=topic,
        defaults={'status': 'completed', 'percentage': 100}
    )
    
    if not created and progress.status != 'completed':
        progress.status = 'completed'
        progress.percentage = 100
        progress.save()
    
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='progress_update',
        object_type='topic',
        object_id=topic.id,
        description=f'"{topic.title}" mavzusini o\'qib bo\'ldi',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'"{topic.title}" mavzusi o\'qilganlar ro\'yxatiga qo\'shildi!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


class HistoricalFigureListView(ListView):
    model = HistoricalFigure
    template_name = 'history/figure_list.html'
    context_object_name = 'figures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HistoricalFigure.objects.filter(is_active=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(biography__icontains=search_query) |
                Q(achievements__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class HistoricalFigureDetailView(DetailView):
    model = HistoricalFigure
    template_name = 'history/figure_detail.html'
    context_object_name = 'figure'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        figure = self.get_object()
        
        # Get related topics
        related_topics = figure.related_topics.filter(is_active=True)
        
        # Get related events
        related_events = figure.events.all()
        
        context.update({
            'related_topics': related_topics,
            'related_events': related_events,
            'breadcrumbs': [
                {'title': 'Tarixiy shaxslar', 'url': '/history/figures/'},
                {'title': figure.name, 'url': figure.get_absolute_url()},
            ]
        })
        return context


class EventListView(ListView):
    model = Event
    template_name = 'history/event_list.html'
    context_object_name = 'events'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Event.objects.all()
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by importance
        importance = self.request.GET.get('importance')
        if importance:
            queryset = queryset.filter(importance=importance)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Date range filter
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        if year_from:
            queryset = queryset.filter(date__year__gte=year_from)
        if year_to:
            queryset = queryset.filter(date__year__lte=year_to)
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['importance_choices'] = Event.IMPORTANCE_CHOICES
        context['search_query'] = self.request.GET.get('q', '')
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'history/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Get related topics and figures
        related_topics = event.related_topics.filter(is_active=True)
        related_figures = event.related_figures.all()
        
        context.update({
            'related_topics': related_topics,
            'related_figures': related_figures,
            'breadcrumbs': [
                {'title': 'Tarixiy voqealar', 'url': '/history/events/'},
                {'title': event.title, 'url': event.get_absolute_url()},
            ]
        })
        return context


class DocumentListView(ListView):
    model = Document
    template_name = 'history/document_list.html'
    context_object_name = 'documents'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Document.objects.all()
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by document type
        doc_type = self.request.GET.get('type')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__icontains=search_query)
            )
        
        # Year range filter
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        if year_from:
            queryset = queryset.filter(year__gte=year_from)
        if year_to:
            queryset = queryset.filter(year__lte=year_to)
        
        return queryset.order_by('-year')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['document_types'] = Document.DOCUMENT_TYPES
        context['search_query'] = self.request.GET.get('q', '')
        return context


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'history/document_detail.html'
    context_object_name = 'document'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = self.get_object()
        
        context.update({
            'breadcrumbs': [
                {'title': 'Tarixiy hujjatlar', 'url': '/history/documents/'},
                {'title': document.title, 'url': document.get_absolute_url()},
            ]
        })
        return context


class HistorySearchView(TemplateView):
    template_name = 'history/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            # Search in topics
            topics = Topic.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query),
                is_active=True
            ).select_related('period', 'period__category')[:10]
            
            # Search in figures
            figures = HistoricalFigure.objects.filter(
                Q(name__icontains=query) |
                Q(biography__icontains=query) |
                Q(achievements__icontains=query),
                is_active=True
            )[:10]
            
            # Search in events
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            
            # Search in documents
            documents = Document.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(content__icontains=query) |
                Q(author__icontains=query)
            )[:10]
            
            context.update({
                'query': query,
                'topics': topics,
                'figures': figures,
                'events': events,
                'documents': documents,
                'total_results': (
                    topics.count() + figures.count() + 
                    events.count() + documents.count()
                )
            })
        
        return context


def categories_processor(request):
    """Context processor for categories"""
    categories = Category.objects.filter(is_active=True).only('name', 'slug', 'icon', 'color')
    return {'categories': categories}