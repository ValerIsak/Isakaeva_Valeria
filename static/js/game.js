const { createApp } = Vue;

createApp({
  data() {
    return {
      task: {},                 // Текущая задача
      questions: [],            // Вопросы внутри задачи
      currentQuestionIndex: 0,  // Индекс текущего вопроса
      answerInput: '',          // Ответ, если вводится вручную
      lives: 0,                 // Кол-во жизней пользователя
      rank: 0,                  // Очки ранга
      hint: '',                 // Текст подсказки
      hintCost: 0,              // Стоимость подсказки
      hintUsed: false,          // Использована ли подсказка
      showHintPopup: false,     // Флаг отображения попапа с подсказкой
      noTasksLeft: false,       // Флаг — есть ли задачи
      flipped: false,           // Перевёрнута ли карточка
      selectedChoice: null,     // Выбранный вариант (если из трёх)
      monsterImage: '',         // Картинка монстра
    };
  },

  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null; // Текущий вопрос
    }
  },

  mounted() {
    // Проверяем, бой ли с боссом
    this.isBossFight = document.getElementById('game-body')?.dataset?.isBoss === 'true';
    const monsterKey = document.getElementById('game-body')?.dataset?.monster;
    if (monsterKey) {
      this.monsterImage = `/static/img/${monsterKey}.jpeg`; // Подгружаем изображение монстра
    }

    this.getStatus();   // Загружаем статус игрока (жизни и очки)
    this.loadTask();    // Загружаем новую задачу
    this.applyBackground(); // Устанавливаем фон локации

    // Убираем затемнение при загрузке
    setTimeout(() => {
        const fade = document.getElementById('game-fade');
        if (fade) {
          fade.classList.add('done');
          setTimeout(() => fade.remove(), 600);
        }
      }, 10);
  },

  methods: {
    // Форматируем математическую формулу для MathJax
    renderedMath(str) {
      return `\\[${str}\\]`;
    },

    // Устанавливаем фон в соответствии с локацией
    applyBackground() {
      const bg = document.getElementById('game-body').dataset.bg;
      document.body.style.background = `url('${bg}') center/cover no-repeat fixed`;
    },

    // Переворот карточки
    flipCard(event) {
      const tag = event?.target?.tagName?.toLowerCase();
      if (['button', 'input'].includes(tag)) return; // Не переворачивать, если клик по input или кнопке

      this.flipped = !this.flipped;

      this.$nextTick(() => {
        if (!this.flipped && window.MathJax && MathJax.typesetPromise) {
          MathJax.typesetClear();      // Очищаем предыдущие формулы
          MathJax.typesetPromise();    // Перерисовываем формулы
        }
      });
    },

    // Выбор варианта ответа
    selectAnswer(option) {
      if (this.selectedChoice === option) {
        this.selectedChoice = null; // Отменить выбор
      } else {
        this.selectedChoice = option;
        this.answerInput = ''; // Очищаем ручной ввод
      }
    },

    // Кнопка "Сохранить" — отправка ответа
    saveAnswer() {
      const trimmed = this.answerInput.trim();
      const result = this.selectedChoice || trimmed;

      if (!result) {
        alert('Вы не выбрали и не ввели ответ!');
        return;
      }

      this.submitAnswer(result);
    },

    // Открыть попап с подсказкой
    openHintPopup() {
      console.log('📦 Клик на Подсказку!');
      this.showHintPopup = true;
    },

    // Закрыть попап с подсказкой
    closeHintPopup() {
      this.showHintPopup = false;
    },

    // Получить текущие жизни и очки ранга
    getStatus() {
      fetch('/game/api/status/')
        .then(res => res.json())
        .then(data => {
          this.lives = data.lives;
          this.rank = data.rank_points;
        });
    },

    // Загрузить новую задачу
    loadTask() {
      fetch('/game/api/task/')
        .then(res => {
          if (res.status === 404) {
            this.noTasksLeft = true; // Нет задач
            return null;
          }
          return res.json();
        })
        .then(data => {
          if (!data) return;

          // Заполняем все данные
          this.task = data;
          this.questions = data.questions;
          this.currentQuestionIndex = 0;
          this.answerInput = '';
          this.hint = data.hint;
          this.hintCost = data.hint_cost;
          this.hintUsed = false;
          this.flipped = false;
          this.selectedChoice = null;

          this.$nextTick(() => {
            if (window.MathJax && window.MathJax.typesetPromise) {
              MathJax.typesetClear();
              MathJax.typesetPromise();
            }
          });
        })
        .catch(err => {
          console.error('Ошибка загрузки задачи:', err);
          this.noTasksLeft = true;
          this.task = {};
          return null;
        });
    },

    // Отправка ответа на сервер
    submitAnswer(answer) {
      const q = this.currentQuestion;
      fetch('/game/api/answer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: q.id, answer: answer })
      })
        .then(res => res.json())
        .then(data => {
          if (data.victory) {
            window.location.href = '/game/boss-victory/'; // Победа над боссом
          } else if (data.boss_defeat) {
            window.location.href = '/game/boss-death/';   // Поражение от босса
          } else if (data.defeat) {
            window.location.href = '/game/defeat/';       // Проигрыш обычный
          } else if (data.correct === false) {
            window.location.href = '/game/choose-location/'; // Неверный ответ
          } else if (data.correct === true) {
            // Если остались вопросы — показываем следующий
            if (this.currentQuestionIndex < this.questions.length - 1) {
              this.currentQuestionIndex++;
              this.answerInput = '';
              this.selectedChoice = null;
            } else {
              // Все вопросы решены — обновляем задачу
              this.task = {};
              this.questions = [];
              this.currentQuestionIndex = 0;
              this.answerInput = '';
              this.selectedChoice = null;

              this.getStatus();
              this.loadTask();
            }
          }
        });
    },

    // Покупка подсказки
    buyHint() {
      fetch('/game/api/hint/', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            this.hintUsed = true;  // Устанавливаем флаг, что подсказка активна
            this.getStatus();      // Обновляем очки ранга
          } else {
            alert('Недостаточно очков ранга');
          }
        });
    },

    // Переход в меню выбора локации
    goToMenu() {
      window.location.href = '/game/choose-location/';
    }
  }
}).mount('#game');
