/* ===== يدعم .sidenav أو .sidebar + .menu-toggle أو .menu-btn ===== */
const drawer  = document.querySelector('.sidenav, .sidebar');
const openBtn = document.querySelector('.menu-toggle, .menu-btn');
const closeBtn= document.querySelector('.close-nav, .close-btn');

let backdrop = document.querySelector('.backdrop');
if (!backdrop) {
  backdrop = document.createElement('div');
  backdrop.className = 'backdrop';
  backdrop.hidden = true;
  document.body.appendChild(backdrop);
}

function openNav(){
  if (!drawer) return;
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden','false');
  openBtn?.setAttribute('aria-expanded','true');
  document.documentElement.classList.add('no-scroll');
  document.body.classList.add('no-scroll');
  backdrop.hidden = false;
}

function closeNav(){
  if (!drawer) return;
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden','true');
  openBtn?.setAttribute('aria-expanded','false');
  document.documentElement.classList.remove('no-scroll');
  document.body.classList.remove('no-scroll');
  backdrop.hidden = true;
}

openBtn?.addEventListener('click', openNav);
closeBtn?.addEventListener('click', closeNav);
backdrop?.addEventListener('click', closeNav);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNav(); });

// أغلق عند الضغط على أي رابط داخل القائمة
drawer?.addEventListener('click', e => {
  const link = e.target.closest('a');
  if (link) closeNav();
});

// أغلق عند تغيير المقاس/الاتجاه
['resize','orientationchange'].forEach(evt =>
  window.addEventListener(evt, () => {
    if (drawer?.classList.contains('open')) closeNav();
  })
);

// سنة الفوتر
document.getElementById('year')?.append(new Date().getFullYear());