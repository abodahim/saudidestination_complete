// تحديث السنة تلقائياً في الفوتر
document.addEventListener("DOMContentLoaded", () => {
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});

// تأثير ظهور بسيط للبطاقات أثناء التمرير
window.addEventListener("scroll", () => {
  document.querySelectorAll(".card").forEach(card => {
    const rect = card.getBoundingClientRect();
    if (rect.top < window.innerHeight - 50) card.classList.add("visible");
  });
});