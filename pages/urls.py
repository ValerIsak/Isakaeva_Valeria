from django.urls import path
from .views import welcome_view, lore_view, rules_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', welcome_view, name='welcome'),
    path('lore/', lore_view, name='lore'),
    path('rules/', rules_view, name='rules'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)