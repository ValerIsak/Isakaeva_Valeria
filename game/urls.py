from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

# Импорт вьюшек из текущего приложения
from .views import (
    choose_monster_view, choose_location_view, play_view, 
    boss_locked_view, theory_page_view, boss_intro_view, 
    boss_death_view, boss_victory_view,
    api_answer, api_hint, api_status, api_task, 
    api_theory_answer, api_theory_question
)

# Пространство имён для приложения game
app_name = 'game'

# Основные игровые маршруты
urlpatterns = [
    path('choose-monster/', choose_monster_view, name='choose_monster'),  # выбор монстра
    path('choose-location/', choose_location_view, name='choose_location'),  # выбор локации
    path('play/', play_view, name='play'),  # основной экран игры

    path('boss-intro/', boss_intro_view, name='boss_intro'),  # вступление перед боем с боссом
    path('boss-locked/', boss_locked_view, name='boss_locked'),  # экран блокировки босса
    path('boss-victory/', boss_victory_view, name='boss_victory'),  # победа над боссом
    path('boss-death/', boss_death_view, name='boss_death'),  # проигрыш в бою с боссом

    path('defeat/', theory_page_view, name='theory_page'),  # страница теории после проигрыша

    # API endpoints
    path('api/status/', api_status, name='api_status'),  # получить текущий статус игрока
    path('api/task/', api_task, name='api_task'),  # получить текущую задачу
    path('api/answer/', api_answer, name='api_answer'),  # отправка ответа на вопрос
    path('api/hint/', api_hint, name='api_hint'),  # получить подсказку

    path('api/theory/', api_theory_question, name='api_theory_question'),  # получить теоретический вопрос
    path('api/theory-answer/', api_theory_answer, name='api_theory_answer'),  # отправить ответ на теоретический вопрос
]

# Добавление маршрутов для отдачи медиафайлов в режиме отладки
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
