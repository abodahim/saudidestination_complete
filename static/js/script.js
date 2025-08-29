// قائمة الجوال
const menuToggle = document.getElementById('menuToggle');
const mainMenu = document.getElementById('mainMenu');
if (menuToggle && mainMenu) {
  menuToggle.addEventListener('click', () => {
    mainMenu.classList.toggle('open');
  });
}

// حساب السعر في صفحة الحجز
(function(){
  const sel   = document.getElementById('tripSelect');
  const days  = document.getElementById('daysInput');
  const total = document.getElementById('totalVal');

  function calc(){
    if (!sel || !days || !total) return;
    const p = parseInt(sel.selectedOptions[0]?.dataset?.price || '0', 10);
    const d = Math.max(1, Math.min(7, parseInt(days.value || '1', 10)));
    total.textContent = (p * d).toLocaleString('ar-SA');
  }
  if (sel) sel.addEventListener('change', calc);
  if (days) days.addEventListener('input', calc);
  calc();
})();
