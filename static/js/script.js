// القائمة الجانبية للموبايل
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("menuToggle");
  const nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      nav.classList.toggle("open");
    });
  }

  // تحديث سعر الرحلة حسب الاختيار في صفحة الحجز
  const tripSelect = document.getElementById("tripSelect");
  const tripPrice = document.getElementById("tripPrice");
  function updatePrice() {
    if (!tripSelect || !tripPrice) return;
    const opt = tripSelect.options[tripSelect.selectedIndex];
    const price = opt?.getAttribute("data-price") || "";
    tripPrice.value = price ? `${price} ر.س` : "";
  }
  if (tripSelect) {
    updatePrice();
    tripSelect.addEventListener("change", updatePrice);
  }
});