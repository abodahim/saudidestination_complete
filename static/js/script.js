const sidebar = document.querySelector('.sidebar');
const menuBtn = document.querySelector('.menu-btn');
const closeBtn = document.querySelector('.close-btn');

let backdrop = document.querySelector('.backdrop');
if (!backdrop) {
  backdrop = document.createElement('div');
  backdrop.className = 'backdrop';
  backdrop.style.display = 'none';
  document.body.appendChild(backdrop);
}

function openMenu() {
  sidebar.classList.add('open');
  document.body.classList.add('menu-open');
  backdrop.style.display = 'block';
}

function closeMenu() {
  sidebar.classList.remove('open');
  document.body.classList.remove('menu-open');
  backdrop.style.display = 'none';
}

menuBtn.addEventListener('click', openMenu);
closeBtn.addEventListener('click', closeMenu);
backdrop.addEventListener('click', closeMenu);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && sidebar.classList.contains('open')) closeMenu();
});

sidebar.addEventListener('click', (e) => {
  const link = e.target.closest('a');
  if (link) closeMenu();
});

['resize', 'orientationchange'].forEach(evt =>
  window.addEventListener(evt, () => {
    if (sidebar.classList.contains('open')) closeMenu();
  })
);