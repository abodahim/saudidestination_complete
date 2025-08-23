// فتح/إغلاق القائمة في الجوال
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("menuToggle");
  const nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      nav.classList.toggle("open");
    });
  }

  // تحديث السعر في صفحة الحجز
  const tripSelect = document.getElementById("tripSelect");
  const priceBox = document.getElementById("priceBox");
  if (tripSelect && priceBox) {
    const updatePrice = () => {
      const opt = tripSelect.options[tripSelect.selectedIndex];
      const price = opt.getAttribute("data-price");
      priceBox.value = `${price} ر.س`;
    };
    tripSelect.addEventListener("change", updatePrice);
    updatePrice();
  }

  // تحقق بسيط للنموذج
  const bookingForm = document.getElementById("bookingForm");
  if (bookingForm) {
    bookingForm.addEventListener("submit", (e) => {
      const email = bookingForm.querySelector('input[name="email"]').value.trim();
      const phone = bookingForm.querySelector('input[name="phone"]').value.trim();
      if (!email.includes("@")) {
        alert("يرجى إدخال بريد إلكتروني صحيح.");
        e.preventDefault();
      }
      if (!/^[0-9]{10}$/.test(phone) || !phone.startsWith("05")) {
        alert("يرجى إدخال رقم جوال سعودي صحيح يبدأ بـ 05.");
        e.preventDefault();
      }
    });
  }
});