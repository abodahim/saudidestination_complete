// ===== منيو الجوال (قائمة جانبية) =====
(function () {
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('mainNav');
  const backdrop = document.getElementById('navBackdrop');

  function openMenu() {
    nav.classList.add('is-open');
    backdrop.hidden = false;
    document.body.classList.add('noscroll');
    toggle.setAttribute('aria-expanded', 'true');
  }
  function closeMenu() {
    nav.classList.remove('is-open');
    backdrop.hidden = true;
    document.body.classList.remove('noscroll');
    toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle && nav && backdrop) {
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (nav.classList.contains('is-open')) closeMenu();
      else openMenu();
    });
    backdrop.addEventListener('click', closeMenu);
    // أغلق عند الضغط على أي رابط داخل المنيو
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    // Esc لإغلاق
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) closeMenu();
    });
  }
})();

// ===== نموذج الحجز: تحديث السعر تلقائياً من القائمة =====
(function () {
  const select = document.querySelector('[data-trip-select]');
  const priceInput = document.querySelector('[data-trip-price]');
  if (!select || !priceInput) return;

  function updatePrice() {
    const opt = select.options[select.selectedIndex];
    const price = opt.getAttribute('data-price') || '';
    priceInput.value = price ? `${price} ر.س` : '';
  }
  select.addEventListener('change', updatePrice);
  updatePrice();
})();