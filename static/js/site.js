// فتح/إغلاق قائمة الجوال
const navToggle = document.getElementById('navToggle');
const mobileNav = document.getElementById('mobileNav');
if (navToggle && mobileNav) {
  navToggle.addEventListener('click', () => {
    mobileNav.classList.toggle('d-none');
  });
}

// حسبة السعر في الحجز
function updateBookingTotal() {
  const price = Number(document.getElementById('pricePerDay')?.value || 0);
  const days = Number(document.getElementById('daysInput')?.value || 1);
  const total = price * Math.max(1, Math.min(7, days));
  const slot = document.getElementById('totalVal');
  if (slot) slot.textContent = total.toLocaleString('ar-SA');
}
const tripSelect = document.getElementById('tripSelect');
const pricePerDay = document.getElementById('pricePerDay');
const daysInput = document.getElementById('daysInput');

if (tripSelect && pricePerDay) {
  tripSelect.addEventListener('change', e => {
    const sel = e.target.selectedOptions[0];
    const p = sel?.dataset?.price || 0;
    pricePerDay.value = p;
    updateBookingTotal();
  });
}
if (daysInput) daysInput.addEventListener('input', updateBookingTotal);
updateBookingTotal();
