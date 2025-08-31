/* ===== قائمة الموبايل ===== */
const menuBtn = document.querySelector('.menu-btn');
const topNav  = document.querySelector('.top-nav');
if (menuBtn && topNav){
  menuBtn.addEventListener('click', ()=>{
    topNav.classList.toggle('is-open');
    document.body.style.overflow = topNav.classList.contains('is-open') ? 'hidden' : '';
  });
}

/* تمرير سلس للروابط داخل الصفحة (اختياري) */
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el){
      e.preventDefault();
      el.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
});