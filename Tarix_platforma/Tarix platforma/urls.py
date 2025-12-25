from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('users/', include('apps.users.urls', namespace='users')),
    path('history/', include('apps.history.urls', namespace='history')),
    path('tests/', include('apps.testsystem.urls', namespace='testsystem')),
    path('progress/', include('apps.progress.urls', namespace='progress')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site settings
admin.site.site_header = 'Tarix Platformasi Boshqaruvi'
admin.site.site_title = 'Tarix Platformasi'
admin.site.index_title = 'Boshqaruv paneli'