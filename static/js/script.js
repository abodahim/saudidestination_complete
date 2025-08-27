// ========== Mobile nav toggle ==========
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('menu-toggle');
  const nav = document.getElementById('nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }
  document.addEventListener('click', (e) => {
    if (!nav || !toggle) return;
    const clickInside = nav.contains(e.target) || toggle.contains(e.target);
    if (!clickInside) nav.classList.remove('open');
  });
});

// ========== Booking form interactions ==========
(function () {
  const select = document.getElementById('tripSelect');
  const daysInput = document.getElementById('daysInput');
  const pricePerDay = document.getElementById('pricePerDay');
  const totalAmount = document.getElementById('totalAmount');
  const agree = document.getElementById('agree');
  const submitBtn = document.getElementById('submitBtn');

  function currency() {
    const h = document.documentElement;
    return h.getAttribute('data-currency') || 'ر.س';
  }
  function clampDays(v) {
    v = Number(v || 1);
    if (v < 1) v = 1;
    if (v > 7) v = 7;
    return v;
  }
  function recompute() {
    if (!select || !daysInput || !pricePerDay || !totalAmount) return;
    const opt = select.options[select.selectedIndex];
    const price = opt ? Number(opt.dataset.price || 0) : 0;
    const days = clampDays(daysInput.value);
    daysInput.value = days;
    pricePerDay.value = `${price} ${currency()}`;
    totalAmount.value = (price * days).toLocaleString('ar-SA') + ' ' + currency();
    if (submitBtn) submitBtn.disabled = !(select.value && days >= 1 && agree && agree.checked);
  }
  if (select) select.addEventListener('change', recompute);
  if (daysInput) daysInput.addEventListener('input', recompute);
  if (agree) agree.addEventListener('change', recompute);
  document.querySelectorAll('[data-step]').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = Number(btn.dataset.step || 0);
      daysInput.value = clampDays((Number(daysInput.value || 1)) + step);
      recompute();
    });
  });
  recompute();
})();

// ========== Simple slider for guides ==========
(function () {
  const slider = document.querySelector('#guidesSlider.slider');
  if (!slider) return;

  // إعداد أساسي: عرض 3 كروت على الشاشات الكبيرة، 2 متوسطة، 1 موبايل
  function slidesPerView() {
    const w = window.innerWidth;
    if (w >= 1100) return 3;
    if (w >= 720) return 2;
    return 1;
  }

  let current = 0;
  function update() {
    const per = slidesPerView();
    const slides = slider.querySelectorAll('.slide');
    const total = slides.length;
    const widthPercent = 100 / per;

    slider.style.display = 'grid';
    slider.style.gridTemplateColumns = `repeat(${total}, 1fr)`;
    slider.style.gap = '16px';
    slider.style.scrollBehavior = 'smooth';
    slider.style.overflow = 'hidden';

    slides.forEach(s => {
      s.style.minWidth = `${widthPercent}%`;
    });

    const offset = current * (slider.clientWidth / per);
    slider.scrollTo({ left: offset, behavior: 'smooth' });
  }

  function clamp() {
    const per = slidesPerView();
    const total = slider.querySelectorAll('.slide').length;
    const maxIndex = Math.max(0, total - per);
    if (current < 0) current = 0;
    if (current > maxIndex) current = maxIndex;
  }

  function next() { current += 1; clamp(); update(); }
  function prev() { current -= 1; clamp(); update(); }

  // أزرار التحكم
  document.querySelectorAll('.slider-next').forEach(btn => {
    if (btn.dataset.target === '#guidesSlider') btn.addEventListener('click', next);
  });
  document.querySelectorAll('.slider-prev').forEach(btn => {
    if (btn.dataset.target === '#guidesSlider') btn.addEventListener('click', prev);
  });

  window.addEventListener('resize', update, { passive: true });
  update();
})();

// ========== Trips filters (client-side) ==========
(function () {
  const grid = document.getElementById('tripsGrid');
  const city = document.getElementById('filterCity');
  const maxPrice = document.getElementById('filterMaxPrice');
  const query = document.getElementById('filterQuery');
  const apply = document.getElementById('applyFilters');
  const reset = document.getElementById('resetFilters');

  if (!grid || !apply || !reset) return;

  function normalize(s) {
    return (s || '').toString().trim().toLowerCase();
  }

  function applyFilters() {
    const c = normalize(city && city.value);
    const mp = Number(maxPrice && maxPrice.value ? maxPrice.value : NaN);
    const q = normalize(query && query.value);

    grid.querySelectorAll('.trip-card').forEach(card => {
      const cardCity = normalize(card.dataset.city);
      const cardName = normalize(card.dataset.name);
      const cardPrice = Number(card.dataset.price || 0);

      let ok = true;
      if (c && cardCity !== c) ok = false;
      if (!isNaN(mp) && mp > 0 && cardPrice > mp) ok = false;
      if (q && !cardName.includes(q)) ok = false;

      card.style.display = ok ? '' : 'none';
    });
  }

  function resetFilters() {
    if (city) city.value = '';
    if (maxPrice) maxPrice.value = '';
    if (query) query.value = '';
    grid.querySelectorAll('.trip-card').forEach(card => card.style.display = '');
  }

  apply.addEventListener('click', applyFilters);
  reset.addEventListener('click', resetFilters);
})();