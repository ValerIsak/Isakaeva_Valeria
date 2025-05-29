from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Location
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task, TheoryQuestion, Question
import json
import random
from django.views.decorators.http import require_POST
from django.db.models import Count


# Словарь сложности монстров
MONSTERS = {
    'kitsune': {'name': 'Кицуне', 'difficulty': 'easy'},
    'cerberus': {'name': 'Цербер', 'difficulty': 'medium'},
    'godzilla': {'name': 'Годзилла', 'difficulty': 'boss', 'min_rank': 40},
}

# Представление для выбора монстра
@login_required
def choose_monster_view(request):
    user = request.user # Получаем текущего авторизованного пользователя

    if request.method == 'POST':
        monster_key = request.POST.get('monster') # Получаем ключ выбранного монстра из формы
        
        # Если монстр не найден в списке, происходит редирект на ту же страницу
        if monster_key not in MONSTERS:
            return redirect('game:choose_monster')

        monster = MONSTERS[monster_key]

        # Если монстр — босс и у пользователя недостаточно очков ранга, отправляем его на экран блокировки
        if monster['difficulty'] == 'boss' and user.rank_points < monster['min_rank']:
            return redirect('game:boss_locked')

        # Устанавливаем выбранного монстра для пользователя
        user.current_monster = monster_key
        user.tasks_solved_in_boss_fight = 0 # Сбрасываем прогресс боя с боссом
        user.is_fighting_boss = monster['difficulty'] == 'boss' # Флаг режима боя с боссом
        user.save()

        # Если выбран босс, отправляем пользователя на вступление
        if monster['difficulty'] == 'boss':
            return redirect('game:boss_intro')

        # В остальных случаях — на выбор локации
        return redirect('game:choose_location')

    # Если GET-запрос — отрисовываем HTML-шаблон выбора монстра
    return render(request, 'game/choose_monster.html', {'monsters': MONSTERS})


# Представление, отображающее экран блокировки босса
@login_required
def boss_locked_view(request):
    return render(request, 'game/boss_locked.html')


# Представление для выбора локации пользователем
@login_required
def choose_location_view(request):
    # Получаем текущего выбранного монстра у пользователя
    monster = request.user.current_monster
    
    # Если монстр не выбран — перенаправляем обратно на страницу выбора монстра
    if not monster:
        return redirect('game:choose_monster')
    
    # Получаем все доступные локации из базы данных
    locations = Location.objects.all()

    # Обработка формы при выборе локации
    if request.method == 'POST':
        location_id = request.POST.get('location')

        # Сохраняем выбранную локацию пользователю
        request.user.current_location = location_id
        request.user.save()
        # Переход к игровому этапу
        return redirect('game:play')
    
    # Отображаем шаблон с выбором локации
    return render(request, 'game/choose_location.html', {'locations': locations})



# Основной игровой интерфейс
@login_required
def play_view(request):
    user = request.user

    # Если монстр не выбран или не выбрана локация (а это не бой с боссом) — отправляем назад
    if not user.current_monster or (not user.current_location and not user.is_fighting_boss):
        return redirect('game:choose_monster')

    # Если у пользователя закончились жизни — отправляем на страницу теории
    if user.lives <= 0:
        return redirect('game:theory_page')

    # Определяем фон локации
    if user.is_fighting_boss:
        # Для босса — статичный фон
        location_background = '/static/img/locations/bg-boss.jpg'
    else:
        # Для обычной локации — пробуем получить изображение из модели Location
        try:
            location = Location.objects.get(name=user.current_location)
            location_background = location.background_image.url if location.background_image else ''
        except Location.DoesNotExist:
            location_background = '' # Если локация не найдена — пустой фон

    # Рендерим страницу игры
    return render(request, 'game/play.html', {
        'location_background': location_background,
        'current_monster': user.current_monster,
        'is_boss_fight': user.is_fighting_boss
    })



# Интерфейс теоретических вопросов
@login_required
def theory_page_view(request):
    return render(request, 'game/theory.html')


# Представление вступления перед боем с боссом
@login_required
def boss_intro_view(request):
    if request.method == 'POST':
        # Обновляем статус пользователя: начинается бой с боссом
        user = request.user
        user.is_fighting_boss = True
        user.tasks_solved_in_boss_fight = 0 # Сброс решённых задач
        user.save()
        # После подтверждения — переход к основному бою
        return redirect('game:play')
    # Отображение вступительной страницы
    return render(request, 'game/boss_intro.html')


# Представление экрана победы над боссом
@login_required
def boss_victory_view(request):
    return render(request, 'game/boss_victory.html')

# Представление экрана поражения в бою с боссом
@login_required
def boss_death_view(request):
    return render(request, 'game/boss_death.html')





# API для Vue.js


# API-эндпоинт, возвращающее текущий статус игрока:
# количество жизней и очков ранга
@login_required
def api_status(request):
    user = request.user
    return JsonResponse({
        'lives': user.lives, # Текущее количество жизней
        'rank_points': user.rank_points # Текущее количество очков ранга
    })


# API-эндпоинт, возвращающий задачу для игрока
@login_required
def api_task(request):
    user = request.user

    task = None # Задача, которую мы вернём

    # Если идёт бой с боссом, подбираем сложные задачи (на 2–3 вопроса)
    if user.is_fighting_boss:
        unsolved = Task.objects.exclude(
            id__in=user.solved_tasks.values_list('id', flat=True) # Исключаем уже решённые задачи
        ).annotate(q_count=Count('questions')) # Считаем количество вопросов у задачи

        tasks_3 = list(unsolved.filter(q_count=3)) # Сначала ищем из 3 вопросов
        tasks_2 = list(unsolved.filter(q_count=2)) # Потом из 2 если не хватает из 3

        tasks_pool = tasks_3 + tasks_2

        if not tasks_pool:
            return JsonResponse({'error': 'Нет новых задач'}, status=404)

        task = random.choice(tasks_pool) # Выбираем случайную из подходящих


    # Если обычный бой — берём монстра, локацию и подбираем соответствующие задачи
    else:
        # Получаем данные о текущем монстре пользователя
        monster = MONSTERS.get(user.current_monster)

        # Если монстр не выбран — возвращаем ошибку
        if not monster:
            return JsonResponse({'error': 'Монстр не выбран'}, status=400)
        
        # Извлекаем уровень сложности, связанный с этим монстром
        difficulty = monster['difficulty']

        # Пытаемся получить объект локации по названию, сохранённому у пользователя
        try:
            location = Location.objects.get(name=user.current_location)
        # Если локация не найдена — ошибка
        except Location.DoesNotExist:
            return JsonResponse({'error': 'Локация не найдена'}, status=400)

        # Формируем queryset задач, соответствующих выбранной локации и уровню сложности
        tasks = Task.objects.filter(
            location=location, # Задача должна относиться к выбранной локации
            difficulty=difficulty, # И иметь ту же сложность, что у монстра
            is_for_boss=False # И не быть задачей для боя с боссом
        ).exclude(
            id__in=user.solved_tasks.values_list('id', flat=True) # Исключаем уже решённые задачи
        )

        # Если таких задач нет — возвращаем ошибку
        if not tasks.exists():
            return JsonResponse({'error': 'Нет новых задач'}, status=404)

        # Из оставшихся задач выбираем случайную
        task = random.choice(list(tasks))

    # Сохраняем ID задачи в сессию
    request.session['current_task_id'] = task.id

    # Формируем список вопросов к задаче
    questions = []
    for q in task.questions.all().order_by('order'):
        q_data = {
            'id': q.id,
            'order': q.order,
            'text': q.text,
            'type': q.question_type,
        }
        if q.question_type == 'choice':
            # Если вопрос с вариантами, добавляем список вариантов
            q_data['options'] = list(q.options.values('id', 'text'))
        questions.append(q_data)

    # Возвращаем JSON с задачей
    return JsonResponse({
        'task_id': task.id,
        'text': task.text,
        'additional_info': task.additional_info or '',
        'rank_points': task.rank_points,
        'hint': task.hint or '',
        'hint_cost': task.hint_cost or 0,
        'questions': questions,
        'task_number': user.tasks_solved_in_boss_fight if user.is_fighting_boss else None,
    }, json_dumps_params={'ensure_ascii': False})









# API-эндпоинт для обработки ответов игрока
@csrf_exempt
@login_required
def api_answer(request):
    # получаем текущего пользователя
    user = request.user

    # Пытаемся достать данные из тела запроса (JSON): ID вопроса и ответ
    try:
        data = json.loads(request.body)
        qid = data.get('question_id')
        answer = data.get('answer')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Ошибка разбора JSON'}, status=400)

    # Проверяем, есть ли задача в сессии — она выдаётся через api_task
    task_id = request.session.get('current_task_id')
    if not task_id:
        return JsonResponse({'error': 'ID задачи не найден'}, status=400)

    # Ищем нужный вопрос в рамках этой задачи
    try:
        q = Question.objects.get(id=qid, task_id=task_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Вопрос не найден'}, status=404)

    # Проверяем ответ
    if q.question_type == 'choice':
        # Если вопрос с выбором — сверяем с вариантом, помеченным как is_correct
        is_correct = q.options.filter(id=answer, is_correct=True).exists()
    else:
        # Если текстовый — сравниваем строку, без учёта регистра и пробелов
        is_correct = str(answer).strip().lower() == q.correct_input.strip().lower()


    # Ключ, по которому храним ID правильно отвеченных вопросов этой задачи
    answered_key = f"answered_{task_id}"

    # Если в сессии ещё не создано хранилище для ответов — создаём
    if 'answered_tasks' not in request.session:
        request.session['answered_tasks'] = {}

    # Если для этой задачи ещё не начат список — тоже создаём
    if answered_key not in request.session['answered_tasks']:
        request.session['answered_tasks'][answered_key] = []

    # БОСС
    if user.is_fighting_boss:
        if is_correct:
            # Добавляем ID вопроса в список, если его там ещё нет
            if q.id not in request.session['answered_tasks'][answered_key]:
                request.session['answered_tasks'][answered_key].append(q.id)
                request.session.modified = True

            # Получаем все ID вопросов задачи
            all_q_ids = list(q.task.questions.values_list('id', flat=True))
            answered = request.session['answered_tasks'][answered_key]


            # Если все вопросы закрыты — задача решена
            if all(qid in answered for qid in all_q_ids):
                user.tasks_solved_in_boss_fight += 1 # +1 к прогрессу по боссу
                user.solved_tasks.add(q.task) # сохраняем задачу как решённую
                del request.session['answered_tasks'][answered_key]
                request.session.modified = True

                # Если решено 3 — победа над боссом
                if user.tasks_solved_in_boss_fight >= 3:
                    user.is_fighting_boss = False
                    user.tasks_solved_in_boss_fight = 0
                    user.save()
                    return JsonResponse({'victory': True})

                user.save()
                # Возвращаем ответ фронтэнду
                return JsonResponse({'correct': True, 'task_completed': True})

            return JsonResponse({'correct': True})

        else:
            # Ошибка — игрок проиграл бой с боссом. Обнуляем всё.
            user.lives = 5
            user.rank_points = 0
            user.current_monster = None
            user.current_location = None
            user.is_fighting_boss = False
            user.tasks_solved_in_boss_fight = 0
            user.solved_tasks.clear()
            user.theory_questions_seen.clear()


            request.session['answered_tasks'].pop(answered_key, None)
            request.session.modified = True

            user.save()
            return JsonResponse({'boss_defeat': True})

#обычные монстры
    if is_correct:
        # Добавляем ID вопроса, если он ещё не добавлен
        if q.id not in request.session['answered_tasks'][answered_key]:
            request.session['answered_tasks'][answered_key].append(q.id)
            request.session.modified = True

        # Проверяем: все ли вопросы решены
        all_q_ids = list(q.task.questions.values_list('id', flat=True))
        answered = request.session['answered_tasks'][answered_key]

        if all(qid in answered for qid in all_q_ids):
            user.add_points(q.task.rank_points) # начисляем очки
            user.solved_tasks.add(q.task) # помечаем задачу как решённую
            del request.session['answered_tasks'][answered_key]
            request.session.modified = True
            user.save()
            return JsonResponse({'correct': True, 'task_completed': True})

        return JsonResponse({'correct': True})

    # Если ответ неверный — засчитываем как "пропущенную" и минус жизнь
    else:
        user.solved_tasks.add(q.task)
        user.lose_life()
        user.refresh_from_db()

        # Чистим сессию по этой задаче
        request.session['answered_tasks'].pop(answered_key, None)
        request.session.modified = True

        if user.lives <= 0:
            user.save()
            return JsonResponse({'defeat': True})

        user.save()
        return JsonResponse({'correct': False})







# API-эндпоинт для подсказки
@csrf_exempt
@login_required
def api_hint(request):
    # Получаем текущего пользователя
    user = request.user

    # Получаем ID текущей задачи из сессии (назначается в api_task)
    task_id = request.session.get('current_task_id')

    # Если ID нет — значит пользователь не начал задачу
    if not task_id:
        return JsonResponse({'error': 'Задача не выбрана'}, status=400)

    # Пытаемся найти задачу по ID
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Задача не найдена'}, status=404)

    # Получаем стоимость подсказки (если None, то ставим 0)
    cost = task.hint_cost or 0

    # Если у пользователя хватает очков, снимаем их и возвращаем успех
    if user.rank_points >= cost:
        user.spend_points(cost) # вызываем метод, который уменьшает очки
        user.save()
        return JsonResponse({'success': True})
    # Если очков недостаточно — ошибка
    return JsonResponse({'error': 'Недостаточно очков'}, status=400)





# API-эндпоинт для теоретических вопросов
@login_required
def api_theory_question(request):
    # Получаем текущего пользователя
    user = request.user
    # Получаем все теоретические вопросы
    all_qs = TheoryQuestion.objects.all()
    # Получаем ID вопросов, которые пользователь уже видел
    seen_ids = user.theory_questions_seen.values_list('id', flat=True)
    # Исключаем уже просмотренные пользователем вопросы
    qs = all_qs.exclude(id__in=seen_ids)

    # Если нет новых вопросов — возвращаем ошибку
    if not qs.exists():
        return JsonResponse({"error": "no_new_questions"}, status=404)

    # Выбираем случайный вопрос из оставшихся
    question = qs.order_by("?").first()

    # Сохраняем правильный ответ и ID вопроса в сессию (для последующей проверки)
    request.session['current_theory_correct'] = question.correct_answer
    request.session['current_theory_id'] = question.id

    # Возвращаем сам вопрос и варианты ответов
    return JsonResponse({
        "question": question.question,
        "answers": [question.answer1, question.answer2, question.answer3]
    })








# API-эндпоинт для обработки ответов на теоретический вопрос
@csrf_exempt
@login_required
@require_POST
def api_theory_answer(request):
    # Парсим тело запроса, извлекаем выбранный пользователем индекс ответа
    data = json.loads(request.body)
    selected_index = data.get("selected") # индекс ответа (0, 1, 2)

    # Достаём из сессии правильный ответ и ID вопроса
    correct = request.session.get("current_theory_correct") # правильный ответ (1, 2 или 3)
    question_id = request.session.get("current_theory_id") # id вопроса в базе

    # Если данных в сессии нет — ошибка
    if correct is None or question_id is None:
        return JsonResponse({"error": "no_correct_in_session"}, status=400)

    # Проверка — правильный ли выбран ответ (selected_index начинается с 0, а correct с 1)
    if int(selected_index) + 1 == correct:
        # Добавляем этот вопрос в список просмотренных
        try:
            question = TheoryQuestion.objects.get(id=question_id)
            request.user.theory_questions_seen.add(question)
        except TheoryQuestion.DoesNotExist:
            pass # если вопрос внезапно удалили — просто игнорим

        # Даём 1 жизнь за правильный ответ
        request.user.lives = 1
        request.user.save()
        return JsonResponse({"correct": True})

    # Если ответ неправильный — возвращаем False
    return JsonResponse({"correct": False})



