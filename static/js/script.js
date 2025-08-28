// حساب السعر الإجمالي وتعبئة سعر اليوم
(function () {
  const tripSelect  = document.getElementById('tripSelect');
  const priceInput  = document.getElementById('pricePerDay');
  const daysInput   = document.getElementById('days');
  const totalEl     = document.getElementById('total');

  function format(n){ return new Intl.NumberFormat('ar-SA').format(n); }

  function recalc() {
    const price = Number(priceInput.value || 0);
    const days  = Number(daysInput?.value || 0);
    const total = price * days;
    if (totalEl) totalEl.textContent = `${format(total)} رس.`;
  }

  function syncPriceFromTrip() {
    if (!tripSelect || !priceInput) return;
    const opt   = tripSelect.options[tripSelect.selectedIndex];
    const price = opt ? Number(opt.getAttribute('data-price') || 0) : 0;
    priceInput.value = price ? price : '';
    recalc();
  }

  if (tripSelect) tripSelect.addEventListener('change', syncPriceFromTrip);
  if (daysInput)  daysInput.addEventListener('input', recalc);

  // تشغيل مبدئي (يدعم حالة قدوم المستخدم بـ ?trip=)
  syncPriceFromTrip();
})();