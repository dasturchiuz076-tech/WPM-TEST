from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivity, UserBookmark

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Test User')
    
    def test_user_profile_creation(self):
        # Profile should be created via signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)


class UserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('users:login')
        self.register_url = reverse('users:register')
        self.profile_url = reverse('users:profile')
    
    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_view_post_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))
    
    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_view_post_success(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        })
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')
    
    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')