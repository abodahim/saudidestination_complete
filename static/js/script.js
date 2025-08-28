// فتح/إغلاق القائمة
document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('menuToggle');
  const menu = document.getElementById('mainMenu');
  if (menuBtn && menu) menuBtn.addEventListener('click', () => menu.classList.toggle('show'));

  // ====== نموذج الحجز ======
  const form = document.getElementById('bookingForm');
  if (form) {
    const tripsData = JSON.parse(form.dataset.trips || '[]');
    const chosen = form.dataset.chosen || '';
    const sel = document.getElementById('tripSelect');
    const priceEl = document.getElementById('pricePerDay');
    const daysEl = document.getElementById('days');
    const totalEl = document.getElementById('total');
    const agree = document.getElementById('agree');
    const submitBtn = document.getElementById('submitBooking');

    const map = Object.fromEntries(tripsData.map(t => [t.slug, t]));
    const updatePrice = () => {
      const slug = sel.value;
      const price = map[slug] ? map[slug].price_per_day : 0;
      const days = Math.max(parseInt(daysEl.value || '1', 10), 1);
      priceEl.value = price + ' ر.س';
      totalEl.textContent = (price * days) || 0;
    };

    // init
    if (chosen && sel) sel.value = chosen;
    updatePrice();

    sel.addEventListener('change', updatePrice);
    daysEl.addEventListener('input', () => {
      let v = parseInt(daysEl.value || '1', 10);
      if (isNaN(v)) v = 1;
      if (v < parseInt(daysEl.min)) v = parseInt(daysEl.min);
      if (v > parseInt(daysEl.max)) v = parseInt(daysEl.max);
      daysEl.value = v;
      updatePrice();
    });

    if (agree && submitBtn) {
      submitBtn.disabled = !agree.checked;
      agree.addEventListener('change', () => submitBtn.disabled = !agree.checked);
    }
  }

  // ====== فلترة الرحلات ======
  const fCity = document.getElementById('fCity');
  const fSort = document.getElementById('fSort');
  const grid = document.getElementById('tripsGrid');
  if (grid && (fCity || fSort)) {
    const cards = Array.from(grid.querySelectorAll('.trip-card'));
    const apply = () => {
      const city = fCity ? fCity.value : '';
      cards.forEach(c => {
        const ok = !city || c.dataset.city === city;
        c.style.display = ok ? '' : 'none';
      });
      const sort = fSort ? fSort.value : '';
      const vis = cards.filter(c => c.style.display !== 'none');
      vis.sort((a,b) => {
        const pa = +a.dataset.price, pb = +b.dataset.price;
        if (sort === 'price_asc') return pa - pb;
        if (sort === 'price_desc') return pb - pa;
        return 0;
      });
      vis.forEach(c => grid.appendChild(c));
    };
    if (fCity) fCity.addEventListener('change', apply);
    if (fSort) fSort.addEventListener('change', apply);
  }

  // ====== PDF للصفحة (إيصال) عبر html2pdf ======
  const btnPdf = document.getElementById('btnPdf');
  const receipt = document.getElementById('receiptArea');
  if (btnPdf && receipt && window.html2pdf) {
    btnPdf.addEventListener('click', () => {
      html2pdf().set({
        margin: 10,
        filename: 'booking-receipt.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(receipt).save();
    });
  }
});