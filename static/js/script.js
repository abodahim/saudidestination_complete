// Saudi Destination – JS (خفيف)
(function () {
  // فتح/إغلاق قائمة الجوال
  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
    });
  }

  // تنقل داخلي سلس
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) { e.preventDefault(); el.scrollIntoView({ behavior: "smooth", block: "start" }); }
      }
    });
  });

  // تهيئة حقل الجوال
  const phone = document.querySelector('input[name="phone"]');
  if (phone) {
    phone.setAttribute("inputmode", "tel");
    phone.addEventListener("input", () => {
      phone.value = phone.value.replace(/[^\d+]/g, "").slice(0, 20);
    });
  }

  // Flash toast (لو حاب تستخدمه لاحقًا)
  const flash = document.getElementById("flash-data");
  if (flash && flash.dataset.msg) {
    const el = document.createElement("div");
    el.className = "toast";
    el.textContent = flash.dataset.msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4200);
  }

  // Lazy Loading بسيط للصور (fallback)
  document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    if ("loading" in HTMLImageElement.prototype) return;
    const src = img.getAttribute("data-src");
    if (src) img.src = src;
  });
})();