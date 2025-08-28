// حساب السعر في صفحة الحجز (إن وُجدت الحقول)
(function(){
  const priceInput = document.querySelector('[data-price-per-day]');
  const daysInput  = document.querySelector('[name="days"]');
  const totalEl    = document.querySelector('[data-total]');

  function recalc(){
    if(!priceInput || !daysInput || !totalEl) return;
    const price = parseInt(priceInput.dataset.pricePerDay || "0", 10);
    const days  = parseInt(daysInput.value || "1", 10);
    totalEl.textContent = (price * days).toLocaleString('ar-EG');
  }

  document.addEventListener('change', (e)=>{
    if(e.target && (e.target.name === 'days' || e.target.name === 'trip')){
      // عند تغيير الرحلة قد تغيّر السعر لليوم
      const chosen = document.querySelector('[data-price-per-day]');
      if(chosen){ chosen.dataset.pricePerDay = chosen.getAttribute('data-price-per-day'); }
      recalc();
    }
  });

  recalc();
})();