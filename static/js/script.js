const toggle = document.querySelector('.menu-toggle');
const sidenav = document.getElementById('sidenav');
const closeBtn = document.querySelector('.close-nav');
const backdrop = document.querySelector('.backdrop');

function openNav(){
  sidenav.classList.add('open');
  sidenav.setAttribute('aria-hidden','false');
  toggle.setAttribute('aria-expanded','true');
  backdrop.hidden = false;
}
function closeNav(){
  sidenav.classList.remove('open');
  sidenav.setAttribute('aria-hidden','true');
  toggle.setAttribute('aria-expanded','false');
  backdrop.hidden = true;
}
toggle?.addEventListener('click', openNav);
closeBtn?.addEventListener('click', closeNav);
backdrop?.addEventListener('click', closeNav);
document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeNav(); });

document.getElementById('year').textContent = new Date().getFullYear();
