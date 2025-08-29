// ===== قائمة الجوال =====
const menuToggle = document.getElementById('menuToggle');
const mainMenu   = document.getElementById('mainMenu');

function closeMenu(){
  if (mainMenu && mainMenu.classList.contains('open')) {
    mainMenu.classList.remove('open');
  }
}

if (menuToggle && mainMenu) {
  // فتح/إغلاق
  menuToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    mainMenu.classList.toggle('open');
  });

  // إغلاق عند الضغط خارج القائمة
  document.addEventListener('click', (e) => {
    if (!mainMenu.contains(e.target) && e.target !== menuToggle) closeMenu();
  });

  // إغلاق بـ Esc
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });

  // إغلاق عند اختيار رابط
  [...mainMenu.querySelectorAll('a')].forEach(a => {
    a.addEventListener('click', () => closeMenu());
  });
}

// ===== حساب السعر في صفحة الحجز =====
(function(){
  const sel   = document.getElementById('tripSelect');
  const days  = document.getElementById('daysInput');
  const total = document.getElementById('totalVal');

  function clamp(val, min, max){
    val = parseInt(val || '0', 10);
    if (isNaN(val)) val = min;
    return Math.max(min, Math.min(max, val));
  }

  function calc(){
    if (!sel || !days || !total) return;
    const price = parseInt(sel.selectedOptions[0]?.dataset?.price || '0', 10);
    const d     = clamp(days.value, 1, 7);
    if (days.value != d) days.value = d;           // ضمان النطاق
    total.textContent = (price * d).toLocaleString('ar-SA');
  }

  if (sel)  sel.addEventListener('change', calc);
  if (days) days.addEventListener('input', calc);
  calc();  // تشغيل أولي
})();