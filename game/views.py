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



MONSTERS = {
    'kitsune': {'name': 'Кицуне', 'difficulty': 'easy'},
    'cerberus': {'name': 'Цербер', 'difficulty': 'medium'},
    'godzilla': {'name': 'Годзилла', 'difficulty': 'boss', 'min_rank': 40},
}

@login_required
def choose_monster_view(request):
    user = request.user

    if request.method == 'POST':
        monster_key = request.POST.get('monster')
        if monster_key not in MONSTERS:
            return redirect('game:choose_monster')

        monster = MONSTERS[monster_key]

        if monster['difficulty'] == 'boss' and user.rank_points < monster['min_rank']:
            return redirect('game:boss_locked')

        user.current_monster = monster_key
        user.tasks_solved_in_boss_fight = 0
        user.is_fighting_boss = monster['difficulty'] == 'boss'
        user.save()

        if monster['difficulty'] == 'boss':
            return redirect('game:boss_intro')


        return redirect('game:choose_location')

    return render(request, 'game/choose_monster.html', {'monsters': MONSTERS})


@login_required
def boss_locked_view(request):
    return render(request, 'game/boss_locked.html')



@login_required
def choose_location_view(request):
    monster = request.user.current_monster
    if not monster:
        return redirect('game:choose_monster')
    locations = Location.objects.all()
    if request.method == 'POST':
        location_id = request.POST.get('location')
        request.user.current_location = location_id
        request.user.save()
        return redirect('game:play')
    return render(request, 'game/choose_location.html', {'locations': locations})




@login_required
def play_view(request):
    user = request.user

    if not user.current_monster or (not user.current_location and not user.is_fighting_boss):
        return redirect('game:choose_monster')

    
    if user.lives <= 0:
        return redirect('game:theory_page')

    if user.is_fighting_boss:
        location_background = '/static/img/locations/bg-boss.jpg'
    else:
        try:
            location = Location.objects.get(name=user.current_location)
            location_background = location.background_image.url if location.background_image else ''
        except Location.DoesNotExist:
            location_background = ''


    return render(request, 'game/play.html', {
        'location_background': location_background,
        'current_monster': user.current_monster,
        'is_boss_fight': user.is_fighting_boss
    })




@login_required
def theory_page_view(request):
    return render(request, 'game/theory.html')



@login_required
def boss_intro_view(request):
    if request.method == 'POST':
        user = request.user
        user.is_fighting_boss = True
        user.tasks_solved_in_boss_fight = 0
        user.save()
        return redirect('game:play')

    return render(request, 'game/boss_intro.html')



@login_required
def boss_victory_view(request):
    return render(request, 'game/boss_victory.html')

@login_required
def boss_death_view(request):
    return render(request, 'game/boss_death.html')





# API

@login_required
def api_status(request):
    user = request.user
    return JsonResponse({
        'lives': user.lives,
        'rank_points': user.rank_points
    })



@login_required
def api_task(request):
    user = request.user

    task = None

    if user.is_fighting_boss:
        unsolved = Task.objects.exclude(
            id__in=user.solved_tasks.values_list('id', flat=True)
        ).annotate(q_count=Count('questions'))

        tasks_3 = list(unsolved.filter(q_count=3))
        tasks_2 = list(unsolved.filter(q_count=2))

        tasks_pool = tasks_3 + tasks_2

        if not tasks_pool:
            return JsonResponse({'error': 'Нет новых задач'}, status=404)

        task = random.choice(tasks_pool)

    else:
        monster = MONSTERS.get(user.current_monster)
        if not monster:
            return JsonResponse({'error': 'Монстр не выбран'}, status=400)

        difficulty = monster['difficulty']

        try:
            location = Location.objects.get(name=user.current_location)
        except Location.DoesNotExist:
            return JsonResponse({'error': 'Локация не найдена'}, status=400)

        tasks = Task.objects.filter(
            location=location,
            difficulty=difficulty,
            is_for_boss=False
        ).exclude(
            id__in=user.solved_tasks.values_list('id', flat=True)
        )

        if not tasks.exists():
            return JsonResponse({'error': 'Нет новых задач'}, status=404)

        task = random.choice(list(tasks))

    request.session['current_task_id'] = task.id

    questions = []
    for q in task.questions.all().order_by('order'):
        q_data = {
            'id': q.id,
            'order': q.order,
            'text': q.text,
            'type': q.question_type,
        }
        if q.question_type == 'choice':
            q_data['options'] = list(q.options.values('id', 'text'))
        questions.append(q_data)

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










@csrf_exempt
@login_required
def api_answer(request):
    user = request.user

    try:
        data = json.loads(request.body)
        qid = data.get('question_id')
        answer = data.get('answer')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Ошибка разбора JSON'}, status=400)

    task_id = request.session.get('current_task_id')
    if not task_id:
        return JsonResponse({'error': 'ID задачи не найден'}, status=400)

    try:
        q = Question.objects.get(id=qid, task_id=task_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Вопрос не найден'}, status=404)


    if q.question_type == 'choice':
        is_correct = q.options.filter(id=answer, is_correct=True).exists()
    else:
        is_correct = str(answer).strip().lower() == q.correct_input.strip().lower()


    answered_key = f"answered_{task_id}"
    if 'answered_tasks' not in request.session:
        request.session['answered_tasks'] = {}

    if answered_key not in request.session['answered_tasks']:
        request.session['answered_tasks'][answered_key] = []


    if user.is_fighting_boss:
        if is_correct:
            if q.id not in request.session['answered_tasks'][answered_key]:
                request.session['answered_tasks'][answered_key].append(q.id)
                request.session.modified = True

            all_q_ids = list(q.task.questions.values_list('id', flat=True))
            answered = request.session['answered_tasks'][answered_key]

            if all(qid in answered for qid in all_q_ids):
                user.tasks_solved_in_boss_fight += 1
                user.solved_tasks.add(q.task)
                del request.session['answered_tasks'][answered_key]
                request.session.modified = True

                if user.tasks_solved_in_boss_fight >= 3:
                    user.is_fighting_boss = False
                    user.tasks_solved_in_boss_fight = 0
                    user.save()
                    return JsonResponse({'victory': True})

                user.save()
                return JsonResponse({'correct': True, 'task_completed': True})

            return JsonResponse({'correct': True})

        else:

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
        if q.id not in request.session['answered_tasks'][answered_key]:
            request.session['answered_tasks'][answered_key].append(q.id)
            request.session.modified = True

        all_q_ids = list(q.task.questions.values_list('id', flat=True))
        answered = request.session['answered_tasks'][answered_key]

        if all(qid in answered for qid in all_q_ids):
            user.add_points(q.task.rank_points)
            user.solved_tasks.add(q.task)
            del request.session['answered_tasks'][answered_key]
            request.session.modified = True
            user.save()
            return JsonResponse({'correct': True, 'task_completed': True})

        return JsonResponse({'correct': True})

    else:
        user.solved_tasks.add(q.task)
        user.lose_life()
        user.refresh_from_db()

        request.session['answered_tasks'].pop(answered_key, None)
        request.session.modified = True

        if user.lives <= 0:
            user.save()
            return JsonResponse({'defeat': True})

        user.save()
        return JsonResponse({'correct': False})








@csrf_exempt
@login_required
def api_hint(request):
    user = request.user
    task_id = request.session.get('current_task_id')

    if not task_id:
        return JsonResponse({'error': 'Задача не выбрана'}, status=400)

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Задача не найдена'}, status=404)

    cost = task.hint_cost or 0

    if user.rank_points >= cost:
        user.spend_points(cost)
        user.save()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Недостаточно очков'}, status=400)






@login_required
def api_theory_question(request):
    user = request.user

    all_qs = TheoryQuestion.objects.all()
    seen_ids = user.theory_questions_seen.values_list('id', flat=True)
    
    qs = all_qs.exclude(id__in=seen_ids)

    if not qs.exists():
        return JsonResponse({"error": "no_new_questions"}, status=404)

    question = qs.order_by("?").first()

    request.session['current_theory_correct'] = question.correct_answer
    request.session['current_theory_id'] = question.id

    return JsonResponse({
        "question": question.question,
        "answers": [question.answer1, question.answer2, question.answer3]
    })









@csrf_exempt
@login_required
@require_POST
def api_theory_answer(request):
    data = json.loads(request.body)
    selected_index = data.get("selected")

    correct = request.session.get("current_theory_correct")
    question_id = request.session.get("current_theory_id")

    if correct is None or question_id is None:
        return JsonResponse({"error": "no_correct_in_session"}, status=400)

    if int(selected_index) + 1 == correct:
        try:
            question = TheoryQuestion.objects.get(id=question_id)
            request.user.theory_questions_seen.add(question)
        except TheoryQuestion.DoesNotExist:
            pass

        request.user.lives = 1
        request.user.save()
        return JsonResponse({"correct": True})

    return JsonResponse({"correct": False})



