from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import choose_monster_view, choose_location_view, play_view, boss_locked_view, theory_page_view, boss_intro_view, boss_death_view, boss_victory_view
from .views import api_answer, api_hint, api_status, api_task, api_theory_answer, api_theory_question

app_name = 'game'

urlpatterns = [
    path('choose-monster/', choose_monster_view, name='choose_monster'),
    path('choose-location/', choose_location_view, name='choose_location'),
    path('play/', play_view, name='play'),
    path('boss-intro/', boss_intro_view, name='boss_intro'),
    path('boss-locked/', boss_locked_view, name='boss_locked'),

    path('boss-victory/', boss_victory_view, name='boss_victory'),
    path('boss-death/', boss_death_view, name='boss_death'),

    path('defeat/', theory_page_view, name='theory_page'),


    path('api/status/', api_status, name='api_status'),
    path('api/task/', api_task, name='api_task'),
    path('api/answer/', api_answer, name='api_answer'),
    path('api/hint/', api_hint, name='api_hint'),
    
    path('api/theory/', api_theory_question, name='api_theory_question'),
    path('api/theory-answer/', api_theory_answer, name='api_theory_answer'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
