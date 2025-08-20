// فتح/إغلاق قائمة الجوال
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menuToggle');
  const list   = document.getElementById('mainNav');

  if (toggle && list) {
    toggle.addEventListener('click', () => {
      list.classList.toggle('open');
    });

    // إغلاق القائمة بعد اختيار رابط
    list.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => list.classList.remove('open'));
    });
  }
});