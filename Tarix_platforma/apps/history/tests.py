from django.test import TestCase
from django.urls import reverse
from .models import Category, Period, Topic


class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Jahon Tarixi',
            slug='world-history',
            description='Jahon tarixi kategoriyasi',
            icon='fas fa-globe',
            color='#3498db'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Jahon Tarixi')
        self.assertEqual(self.category.slug, 'world-history')
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        self.assertEqual(str(self.category), 'Jahon Tarixi')
    
    def test_category_get_absolute_url(self):
        url = reverse('history:category_detail', kwargs={'slug': 'world-history'})
        self.assertEqual(self.category.get_absolute_url(), url)


class PeriodModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Jahon Tarixi',
            slug='world-history'
        )
        self.period = Period.objects.create(
            name='Qadimgi Davr',
            slug='ancient-period',
            category=self.category,
            description='Qadimgi davr tarixi',
            start_year=-3000,
            end_year=500
        )
    
    def test_period_creation(self):
        self.assertEqual(self.period.name, 'Qadimgi Davr')
        self.assertEqual(self.period.category, self.category)
        self.assertEqual(self.period.century, "30-asr")  # -3000/100 + 1 = -30, but we handle it
    
    def test_period_str(self):
        expected_str = "Qadimgi Davr (-3000-500)"
        self.assertEqual(str(self.period), expected_str)


class TopicModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Jahon Tarixi',
            slug='world-history'
        )
        self.period = Period.objects.create(
            name='Qadimgi Davr',
            slug='ancient-period',
            category=self.category,
            start_year=-3000,
            end_year=500
        )
        self.topic = Topic.objects.create(
            title='Qadimgi Misr',
            slug='ancient-egypt',
            period=self.period,
            content='Qadimgi Misr tarixi',
            difficulty='beginner',
            estimated_time=45
        )
    
    def test_topic_creation(self):
        self.assertEqual(self.topic.title, 'Qadimgi Misr')
        self.assertEqual(self.topic.period, self.period)
        self.assertEqual(self.topic.view_count, 0)
        self.assertEqual(self.topic.difficulty, 'beginner')
    
    def test_topic_increment_view_count(self):
        initial_count = self.topic.view_count
        self.topic.increment_view_count()
        self.assertEqual(self.topic.view_count, initial_count + 1)
    
    def test_topic_slug_auto_generation(self):
        topic2 = Topic.objects.create(
            title='Yangi Mavzu',
            period=self.period,
            content='Test content'
        )
        self.assertEqual(topic2.slug, 'yangi-mavzu')


class HistoryViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Jahon Tarixi',
            slug='world-history',
            is_active=True
        )
        self.period = Period.objects.create(
            name='Qadimgi Davr',
            slug='ancient-period',
            category=self.category,
            is_active=True
        )
        self.topic = Topic.objects.create(
            title='Test Mavzu',
            slug='test-topic',
            period=self.period,
            content='Test content',
            is_active=True
        )
    
    def test_category_list_view(self):
        url = reverse('history:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history/category_list.html')
        self.assertContains(response, 'Jahon Tarixi')
    
    def test_period_detail_view(self):
        url = reverse('history:period_detail', kwargs={'slug': 'ancient-period'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history/period_detail.html')
        self.assertContains(response, 'Qadimgi Davr')
    
    def test_topic_detail_view(self):
        url = reverse('history:topic_detail', kwargs={'slug': 'test-topic'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history/topic_detail.html')
        self.assertContains(response, 'Test Mavzu')