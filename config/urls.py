from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('game/', include('game.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)