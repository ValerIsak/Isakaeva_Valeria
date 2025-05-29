from django.urls import path
from .views import SignupPageView, CustomLoginView, logout_view
from django.conf.urls.static import static
from django.conf import settings


app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)