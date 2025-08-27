// Mobile nav toggle
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('menu-toggle');
  const nav = document.getElementById('nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  // Optional: close menu عند الضغط خارجها بالجوال
  document.addEventListener('click', (e) => {
    if (!nav || !toggle) return;
    const clickInside = nav.contains(e.target) || toggle.contains(e.target);
    if (!clickInside) nav.classList.remove('open');
  });
});
