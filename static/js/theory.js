const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,       // Флаг загрузки — true, пока не получим вопрос
      question: '',        // Текст текущего вопроса
      answers: [],         // Массив с вариантами ответа
      answered: false,     // Флаг — был ли уже дан ответ
      resultText: '',      // Текст результата после ответа (правильно/неправильно)
      lives: 0,            // Количество жизней
      rankPoints: 0        // Очки ранга
    };
  },
  methods: {
    // Получение нового вопроса с сервера
    fetchQuestion() {
      fetch('/game/api/theory/')
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            // Если вопросов больше нет
            this.question = 'Вопросы закончились.';
            this.answers = [];
            this.loading = false;
            return;
          }
          // Заполняем данные
          this.question = data.question;
          this.answers = data.answers;
          this.loading = false;
          this.answered = false;
          this.resultText = '';
        });
    },

    // Получение текущего статуса игрока (жизни и очки)
    fetchStatus() {
      fetch('/game/api/status/')
        .then(res => res.json())
        .then(data => {
          this.lives = data.lives;
          this.rankPoints = data.rank_points;
        });
    },

    // Отправка выбранного ответа на сервер
    submitAnswer(index) {
      fetch('/game/api/theory-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken'), // Передаём CSRF-токен
        },
        body: JSON.stringify({ selected: index }) // Выбранный индекс ответа
      })
        .then(res => res.json())
        .then(data => {
          this.answered = true;
          if (data.correct) {
            // Если правильно — показываем результат, прибавляем жизнь и переходим к выбору локации
            this.resultText = 'Верно! Восстановлена 1 жизнь.';
            this.lives += 1;
            setTimeout(() => {
                window.location.href = "/game/choose-location/";
              }, 2000);
          } else {
            // Если неправильно — показываем текст и через 2 сек загружаем следующий вопрос
            this.resultText = 'Неправильно. Следующий вопрос...';
            setTimeout(() => this.fetchQuestion(), 2000);
          }
        });
    },

    // Получение значения куки по имени (для CSRF)
    getCookie(name) {
      const cookies = document.cookie.split(';');
      for (let c of cookies) {
        const cookie = c.trim();
        if (cookie.startsWith(name + '=')) {
          return decodeURIComponent(cookie.split('=')[1]);
        }
      }
      return null;
    }
  },

  // При загрузке компонента сразу получаем вопрос и статус игрока
  mounted() {
    this.fetchQuestion();
    this.fetchStatus();
  }
}).mount('#theory-app');
