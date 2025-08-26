/* ========== قائمة الموبايل البسيطة ========== */
(function () {
  const menu = document.getElementById('mobileMenu');
  const openBtn = document.getElementById('menuToggle');
  const closeBtn = document.getElementById('menuClose');
  const backdrop = document.getElementById('menuBackdrop');

  function open() {
    if (!menu) return;
    menu.classList.add('show');
    backdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    if (!menu) return;
    menu.classList.remove('show');
    backdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (openBtn) openBtn.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (backdrop) backdrop.addEventListener('click', close);

  // أغلق القائمة عند الضغط على أي رابط داخلها
  if (menu) {
    menu.addEventListener('click', function (e) {
      const link = e.target.closest('a');
      if (link) close();
    });
  }
})();

/* ========== تفاعلات نموذج الحجز ========== */
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
    totalAmount.textContent = (price * days).toLocaleString('ar-SA') + ' ' + currency();

    if (submitBtn) {
      submitBtn.disabled = !(select.value && days >= 1 && agree && agree.checked);
    }
  }

  if (select) select.addEventListener('change', recompute);
  if (daysInput) daysInput.addEventListener('input', recompute);
  if (agree) agree.addEventListener('change', recompute);

  // أزرار الزيادة/النقصان
  document.querySelectorAll('.stepper__btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = Number(btn.dataset.step || 0);
      daysInput.value = clampDays((Number(daysInput.value || 1)) + step);
      recompute();
    });
  });

  recompute();
})();