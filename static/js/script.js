// فتح/إغلاق درج القائمة + Overlay
(function () {
  const drawer = document.getElementById('drawer');
  const toggle = document.getElementById('menuToggle');
  const closeBtn = document.getElementById('drawerClose');
  const overlay = document.getElementById('overlay');

  function openDrawer() {
    if (!drawer) return;
    drawer.setAttribute('aria-hidden', 'false');
    drawer.classList.add('open');
    if (overlay) { overlay.hidden = false; overlay.classList.add('show'); }
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    if (!drawer) return;
    drawer.setAttribute('aria-hidden', 'true');
    drawer.classList.remove('open');
    if (overlay) { overlay.classList.remove('show'); overlay.hidden = true; }
    document.body.style.overflow = '';
  }

  toggle && toggle.addEventListener('click', openDrawer);
  closeBtn && closeBtn.addEventListener('click', closeDrawer);
  overlay && overlay.addEventListener('click', closeDrawer);
})();

// منطق نموذج الحجز (عدد الأيام + المجموع)
window.bookingInit = function bookingInit () {
  const tripSelect = document.getElementById('trip');
  const daysInput  = document.getElementById('days');
  const totalEl    = document.getElementById('total');
  const totalInput = document.getElementById('totalInput');
  const decBtn     = document.querySelector('.number__btn[data-op="dec"]');
  const incBtn     = document.querySelector('.number__btn[data-op="inc"]');

  function priceForSelectedTrip() {
    const opt = tripSelect.options[tripSelect.selectedIndex];
    return Number(opt.dataset.price || 0);
  }

  function clampDays() {
    const min = Number(daysInput.min || 1);
    const max = Number(daysInput.max || 7);
    let v = Number(daysInput.value || 1);
    v = Math.max(min, Math.min(max, v));
    daysInput.value = v;
    return v;
  }

  function updateTotal() {
    const price = priceForSelectedTrip();
    const days  = clampDays();
    const total = price * days;
    totalEl.textContent = total.toLocaleString('ar-EG');
    totalInput.value = String(total);
  }

  // أزرار +/-
  decBtn && decBtn.addEventListener('click', () => { daysInput.stepDown(); updateTotal(); });
  incBtn && incBtn.addEventListener('click', () => { daysInput.stepUp();   updateTotal(); });

  tripSelect && tripSelect.addEventListener('change', updateTotal);
  daysInput  && daysInput.addEventListener('input', updateTotal);

  // تشغيل أول حساب
  updateTotal();
};