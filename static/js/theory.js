const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,
      question: '',
      answers: [],
      answered: false,
      resultText: '',
      lives: 0,
      rankPoints: 0
    };
  },
  methods: {
    fetchQuestion() {
      fetch('/game/api/theory/')
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            this.question = 'Вопросы закончились.';
            this.answers = [];
            this.loading = false;
            return;
          }
          this.question = data.question;
          this.answers = data.answers;
          this.loading = false;
          this.answered = false;
          this.resultText = '';
        });
    },
    fetchStatus() {
      fetch('/game/api/status/')
        .then(res => res.json())
        .then(data => {
          this.lives = data.lives;
          this.rankPoints = data.rank_points;
        });
    },
    submitAnswer(index) {
      fetch('/game/api/theory-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken'),
        },
        body: JSON.stringify({ selected: index })
      })
        .then(res => res.json())
        .then(data => {
          this.answered = true;
          if (data.correct) {
            this.resultText = 'Верно! Восстановлена 1 жизнь.';
            this.lives += 1;
            setTimeout(() => {
                window.location.href = "/game/choose-location/";
              }, 2000);
          } else {
            this.resultText = 'Неправильно. Следующий вопрос...';
            setTimeout(() => this.fetchQuestion(), 2000);
          }
        });
    },
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
  mounted() {
    this.fetchQuestion();
    this.fetchStatus();
  }
}).mount('#theory-app');
