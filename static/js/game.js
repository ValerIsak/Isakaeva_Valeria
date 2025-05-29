
const { createApp } = Vue;

createApp({
  data() {
    return {
      task: {},
      questions: [],
      currentQuestionIndex: 0,
      answerInput: '',
      lives: 0,
      rank: 0,
      hint: '',
      hintCost: 0,
      hintUsed: false,
      showHintPopup: false,
      noTasksLeft: false,
      flipped: false,
      selectedChoice: null,
      monsterImage: '',
    };
  },

  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null;
    }
  },

  mounted() {

    this.isBossFight = document.getElementById('game-body')?.dataset?.isBoss === 'true';
    const monsterKey = document.getElementById('game-body')?.dataset?.monster;
    if (monsterKey) {
      this.monsterImage = `/static/img/${monsterKey}.jpeg`;
    }

    this.getStatus();
    this.loadTask();
    this.applyBackground();


    setTimeout(() => {
        const fade = document.getElementById('game-fade');
        if (fade) {
          fade.classList.add('done');
          setTimeout(() => fade.remove(), 600);
        }
      }, 10);

  },

  methods: {
    renderedMath(str) {
      return `\\[${str}\\]`;
      // или `\\(${str}\\)` 
    },
    applyBackground() {
      const bg = document.getElementById('game-body').dataset.bg;
      document.body.style.background = `url('${bg}') center/cover no-repeat fixed`;
    },

    flipCard(event) {
      const tag = event?.target?.tagName?.toLowerCase();
      if (['button', 'input'].includes(tag)) return;

      this.flipped = !this.flipped;

      this.$nextTick(() => {
        if (!this.flipped && window.MathJax && MathJax.typesetPromise) {
          MathJax.typesetClear();
          MathJax.typesetPromise();
        }
      });
    },

      selectAnswer(option) {
        if (this.selectedChoice === option) {
          this.selectedChoice = null;
        } else {
          this.selectedChoice = option;
          this.answerInput = '';
        }
      },

      saveAnswer() {
        const trimmed = this.answerInput.trim();
        const result = this.selectedChoice || trimmed;

        if (!result) {
          alert('Вы не выбрали и не ввели ответ!');
          return;
        }

        this.submitAnswer(result);
      },

      openHintPopup() {
        console.log('📦 Клик на Подсказку!');
        this.showHintPopup = true;
      },

      closeHintPopup() {
        this.showHintPopup = false;
      },

    getStatus() {
      fetch('/game/api/status/')
        .then(res => res.json())
        .then(data => {
          this.lives = data.lives;
          this.rank = data.rank_points;
        });
    },

    loadTask() {
      fetch('/game/api/task/')
        .then(res => {
          if (res.status === 404) {
            this.noTasksLeft = true;
            return null;
          }
          return res.json();
        })
        .then(data => {
          if (!data) return;

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
            window.location.href = '/game/boss-victory/';
          } else if (data.boss_defeat) {
            window.location.href = '/game/boss-death/';
          } else if (data.defeat) {
            window.location.href = '/game/defeat/';
          } else if (data.correct === false) {
            window.location.href = '/game/choose-location/';
          } else if (data.correct === true) {
            if (this.currentQuestionIndex < this.questions.length - 1) {
              this.currentQuestionIndex++;
              this.answerInput = '';
              this.selectedChoice = null;
            } else {
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

    buyHint() {
      fetch('/game/api/hint/', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            this.hintUsed = true;
            this.getStatus();
          } else {
            alert('Недостаточно очков ранга');
          }
        });
    },

    goToMenu() {
      window.location.href = '/game/choose-location/';
    }
  }
}).mount('#game');