/* =========================================================================
   Saudi Destination – Main JS
   - Mobile menu (hamburger)
   - Smooth scroll for in-page anchors
   - Minor helpers for the booking form (price/days handling)
   ========================================================================= */

/* ================ Helpers ================ */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

const lockScroll = (lock = true) => {
  document.documentElement.classList.toggle('no-scroll', lock);
  document.body.classList.toggle('no-scroll', lock);
};

/* ================ Mobile Menu ================ */
(() => {
  const toggleBtn = $('#menuToggle') || $('.nav__toggle');
  const nav = $('#mainNav') || $('.nav__list');
  if (!toggleBtn || !nav) return;

  const OPEN_CLASS = 'is-open';

  const openMenu = () => {
    nav.classList.add(OPEN_CLASS);
    toggleBtn.setAttribute('aria-expanded', 'true');
    lockScroll(true);
  };
  const closeMenu = () => {
    nav.classList.remove(OPEN_CLASS);
    toggleBtn.setAttribute('aria-expanded', 'false');
    lockScroll(false);
  };
  const toggleMenu = () => {
    nav.classList.contains(OPEN_CLASS) ? closeMenu() : openMenu();
  };

  // Init ARIA state
  toggleBtn.setAttribute('aria-controls', nav.id || 'mainNav');
  toggleBtn.setAttribute('aria-expanded', 'false');

  // Click toggle
  toggleBtn.addEventListener('click', (e) => {
    e.preventDefault();
    toggleMenu();
  });

  // Close on link click
  $$('.nav__list a, nav a').forEach((a) =>
    a.addEventListener('click', () => closeMenu())
  );

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (!nav.classList.contains(OPEN_CLASS)) return;
    const isClickInside =
      nav.contains(e.target) || toggleBtn.contains(e.target);
    if (!isClickInside) closeMenu();
  });

  // Close on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });

  // Close on resize to desktop
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 992) closeMenu();
    }, 150);
  });
})();

/* ================ Smooth Scroll for anchors ================ */
(() => {
  const header = $('header.topbar');
  const headerH = () => (header ? header.offsetHeight : 0);

  $$('.js-scroll, a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href') || '';
      if (!href.startsWith('#') || href === '#') return;
      const target = $(href);
      if (!target) return;

      e.preventDefault();

      const top =
        target.getBoundingClientRect().top + window.pageYOffset - headerH() - 8;

      window.scrollTo({
        top,
        behavior: 'smooth',
      });
    });
  });
})();

/* ================ Booking Form Helpers ================ */
(() => {
  const form = $('#bookingForm');
  if (!form) return;

  const tripSelect = $('#tripSelect');
  const priceInput = $('#price');
  const daysInput = $('#days');
  const totalOut = $('#totalPrice');
  const currencyOut = $('#currencySym');

  // Try to preselect by ?trip_id= in URL
  const params = new URLSearchParams(window.location.search);
  const preTrip = params.get('trip_id');
  if (preTrip && tripSelect?.options) {
    const opt = Array.from(tripSelect.options).find(
      (o) => o.value === preTrip || o.dataset.id === preTrip
    );
    if (opt) tripSelect.value = opt.value;
  }

  const normalizeNum = (v, fallback = 1) => {
    const n = parseInt(v, 10);
    return Number.isFinite(n) && n > 0 ? n : fallback;
  };

  const updatePrice = () => {
    if (!tripSelect) return;

    const selOpt = tripSelect.options[tripSelect.selectedIndex];
    if (!selOpt) return;

    const price = Number(selOpt.dataset.price || 0); // price per day
    const currency = selOpt.dataset.currency || 'ر.س';
    const minDays = normalizeNum(selOpt.dataset.minDays || 1, 1);
    const maxDays = normalizeNum(selOpt.dataset.maxDays || 7, 7);

    // Enforce min/max on days
    if (daysInput) {
      daysInput.min = String(minDays);
      daysInput.max = String(maxDays);
      if (!daysInput.value) daysInput.value = String(minDays);
      const d = Math.min(
        Math.max(normalizeNum(daysInput.value, minDays), minDays),
        maxDays
      );
      daysInput.value = String(d);
    }

    // Update unit price text input (readonly)
    if (priceInput) priceInput.value = `${price}`;

    // Update currency label if exists
    if (currencyOut) currencyOut.textContent = currency;

    // Update total
    if (totalOut && daysInput) {
      const d = normalizeNum(daysInput.value, 1);
      totalOut.textContent = `${(price * d).toLocaleString('ar-EG')} ${currency}`;
    }
  };

  tripSelect?.addEventListener('change', updatePrice);
  daysInput?.addEventListener('input', updatePrice);

  // Initial call
  updatePrice();

  // Simple front validation UX
  form.addEventListener('submit', (e) => {
    const required = $$('[required]', form);
    let ok = true;
    required.forEach((el) => {
      if (!el.value?.trim()) {
        ok = false;
        el.classList.add('is-invalid');
      } else {
        el.classList.remove('is-invalid');
      }
    });
    if (!ok) {
      e.preventDefault();
      const first = $('.is-invalid', form);
      first?.focus();
    }
  });
})();

/* ================ Image reveal (optional, graceful) ================ */
(() => {
  if (!('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          en.target.classList.add('in-view');
          io.unobserve(en.target);
        }
      });
    },
    { rootMargin: '0px 0px -10% 0px', threshold: 0.05 }
  );
  $$('.card img, .guide-card img, .hero').forEach((el) => io.observe(el));
})();