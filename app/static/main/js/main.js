(function(){
  const nav = document.querySelector('.navbar-glass');
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 20) nav.classList.add('scrolled'); else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();

(function(){
  const els = document.querySelectorAll('.feature-card, .hero-figure, .about-media');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;
  els.forEach(el => el.classList.add('reveal'));
  const io = new IntersectionObserver(entries=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:.12});
  els.forEach(el=>io.observe(el));
})();

function getCookieValue(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');

    for (let i = 0; i < cookies.length; ++i) {
      const cookie = cookies[i].trim();

      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}

const csrfToken = getCookieValue('csrftoken');

document.querySelectorAll('.js-vote-btn').forEach(button => {
  button.addEventListener('click', function() {
    const container = this.closest('.vote-controls');
    const upBtn = container.querySelector('.upvote');
    const downBtn = container.querySelector('.downvote');
    const action = this.dataset.action;

     if (action === 'like') {
        if (this.classList.contains('active')) {
             this.classList.remove('active');
        } else {
             this.classList.add('active');
             downBtn.classList.remove('active');
        }
    } else if (action === 'dislike') {
        if (this.classList.contains('active')) {
             this.classList.remove('active');
        } else {
             this.classList.add('active');
             upBtn.classList.remove('active');
        }
    }

    this.disabled = true;

    const objectID = button.dataset.id;
    const objectType = button.dataset.type;

    const idetifyPath = `rating-${objectType}-${objectID}`;

    fetch('/ajax/vote/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        object_id: objectID,
        object_type: objectType,
        action: action
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      return response.json();
    })
    .then(data => {
      if (data.rating !== undefined) {
        document.getElementById(idetifyPath).innerText = data.rating;
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
      alert("Что-то пошло не так при голосовании");
    })
    .finally(() => {
        this.disabled = false;
    });
  });
});

document.querySelectorAll('.js-correct-btn').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    const answerId = this.dataset.answerId;
    const isCorrect = this.checked;
    const idetifyPath = `answer-${answerId}`;


     this.disabled = true;

    fetch('/ajax/correct/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        answer_id: answerId,
        is_correct: this.checked
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      return response.json();
    })
    .then(data => {
      if (data.status === 'ok') {
          console.log('Статус обновлен');
          const answerBlock = document.getElementById(idetifyPath);

          if (answerBlock) {
            if (isCorrect) {
                answerBlock.classList.add('correct-answer');
            } else {
                answerBlock.classList.remove('correct-answer');
            }
          }
      } else {
          alert('Ошибка: ' + data.error);
          this.checked = !isCorrect;
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
      alert("Что-то пошло не так при голосовании");
    })
    .finally(() => {
        this.disabled = false;
    });

  });
});

document.addEventListener('DOMContentLoaded', () =>{
  document.querySelectorAll('.js-rating').forEach(el => {
    const objectId = el.dataset.id;
    const objectType = el.dataset.type;

    fetch(`/ajax/vote/?object_id=${objectId}&object_type=${objectType}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      return response.json();
    })
    .then(data => {
      if (data.rating !== undefined) {
        el.innerText = data.rating;

        if (data.value === 1) {
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='like']`).classList.add('active');
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='dislike']`).classList.remove('active');
        } else if (data.value === -1) {
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='dislike']`).classList.add('active');
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='like']`).classList.remove('active');
        } else {
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='dislike']`).classList.remove('active');
          document.querySelector(`[data-id='${objectId}'][data-type='${objectType}'][data-action='like']`).classList.remove('active');
        }
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
      alert("Что-то пошло не так при голосовании");
    })
  });

  document.querySelectorAll('.js-correct-btn').forEach(checkbox => {
    answerId = checkbox.dataset.answerId;

    fetch(`/ajax/correct/?answer_id=${answerId}`)
    .then(response => response.json())
    .then(data => {
      checkbox.checked = data.is_correct;

      const answerBlock = document.getElementById(`answer-${answerId}`);

      if (answerBlock) {
        if (data.is_correct) {
          answerBlock.classList.add('correct-answer');
        } else {
          answerBlock.classList.remove('correct-answer');
        }
      }
    })
    .catch(console.error)
  });
});
