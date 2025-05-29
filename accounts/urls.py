from django.urls import path
from .views import SignupPageView, CustomLoginView, logout_view
from django.conf.urls.static import static
from django.conf import settings

# Пространство имён приложения, используется для обращения к маршрутам через accounts:login и т.п.
app_name = 'accounts'

# Основные маршруты приложения accounts
urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'), # маршрут для регистрации нового пользователя
    path('login/', CustomLoginView.as_view(), name='login'), # маршрут для входа
    path('logout/', logout_view, name='logout'), # маршрут для выхода из аккаунта
]

# Добавляем маршруты для доступа к загруженным медиафайлам (например, изображениям профиля)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)