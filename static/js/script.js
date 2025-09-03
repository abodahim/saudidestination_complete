// static/js/script.js
(function () {
  const btn = document.querySelector('.menu-btn');
  const nav = document.querySelector('.top-nav');
  if (btn && nav) {
    btn.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }
})();