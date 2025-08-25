document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("menuToggle");
  const drawer = document.getElementById("drawer");
  const backdrop = document.getElementById("backdrop");

  if (!toggle || !drawer || !backdrop) return;

  function openDrawer() {
    drawer.classList.add("drawer--open");
    backdrop.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    drawer.classList.remove("drawer--open");
    backdrop.hidden = true;
    document.body.style.overflow = "";
  }

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    if (drawer.classList.contains("drawer--open")) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });

  backdrop.addEventListener("click", closeDrawer);
  drawer.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });

  // إغلاق القائمة عند الضغط على أي رابط داخلها
  drawer.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", closeDrawer);
  });
});