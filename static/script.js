document.addEventListener('DOMContentLoaded', () => {
  // زر القائمة للجوال
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('mainNav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => nav.classList.toggle('show'));
  }
});
