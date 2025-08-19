// فتح/إغلاق قائمة الجوال
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('open');
    });
  }
});

// تمرير سلس للروابط الداخلية (#id)
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const id = a.getAttribute('href').slice(1);
  const el = document.getElementById(id);
  if (el) {
    e.preventDefault();
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

// بديل للصور المفقودة (خصوصاً صور المرشدين)
document.querySelectorAll('img').forEach(img => {
  img.addEventListener('error', () => {
    if (img.alt && img.alt.includes('مرشد')) {
      img.src = '/static/images/guide1.PNG';
    }
  });
});
