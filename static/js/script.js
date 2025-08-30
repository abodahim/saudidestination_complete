// إظهار/إخفاء القائمة على الجوال
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.menu-btn');
  if (!btn) return;
  const nav = document.querySelector('.top-nav');
  if (nav) nav.classList.toggle('is-open');
});

// تحسين تمرير داخلي سلس لأية روابط #anchor
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) {
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});