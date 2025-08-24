// === القائمة الجانبية (تعمل في كل الصفحات) ===
(function () {
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('siteNav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('nav--open');
    });
    // إغلاق عند الضغط خارج القائمة
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && e.target !== toggle) {
        nav.classList.remove('nav--open');
      }
    });
  }
})();

// === نموذج الحجز: حساب السعر والإجمالي + ضبط حدود الأيام ===
(function () {
  const tripSelect = document.getElementById('tripSelect');
  const daysInput = document.getElementById('daysInput');
  const priceCell = document.getElementById('priceCell');
  const totalCell = document.getElementById('totalCell');
  const daysHint = document.getElementById('daysHint');

  function updateFromTrip() {
    if (!tripSelect || !daysInput) return;
    const opt = tripSelect.options[tripSelect.selectedIndex];
    const price = parseInt(opt.getAttribute('data-price'), 10);
    const dmin = parseInt(opt.getAttribute('data-min'), 10);
    const dmax = parseInt(opt.getAttribute('data-max'), 10);
    const ddef = parseInt(opt.getAttribute('data-default'), 10);

    daysInput.min = dmin;
    daysInput.max = dmax;
    if (!daysInput.value) daysInput.value = ddef;
    let days = Math.max(dmin, Math.min(parseInt(daysInput.value || ddef, 10), dmax));
    daysInput.value = days;

    priceCell.textContent = `${price} ر.س`;
    totalCell.textContent = `${price * days} ر.س`;
    daysHint.textContent = `الحد الأدنى ${dmin} والحد الأقصى ${dmax} أيام`;
  }

  function updateTotal() {
    if (!tripSelect || !daysInput) return;
    const opt = tripSelect.options[tripSelect.selectedIndex];
    const price = parseInt(opt.getAttribute('data-price'), 10);
    let days = parseInt(daysInput.value || '1', 10);
    const dmin = parseInt(opt.getAttribute('data-min'), 10);
    const dmax = parseInt(opt.getAttribute('data-max'), 10);
    days = Math.max(dmin, Math.min(days, dmax));
    daysInput.value = days;
    totalCell.textContent = `${price * days} ر.س`;
  }

  if (tripSelect && daysInput) {
    tripSelect.addEventListener('change', updateFromTrip);
    daysInput.addEventListener('input', updateTotal);
    updateFromTrip();
  }
})();