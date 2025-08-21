// فتح/إغلاق قائمة الجوال
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('menuToggle');
  var nav = document.getElementById('mainNav');
  if (toggle && nav) {
    toggle.addEventListener('click', function(){
      nav.classList.toggle('show');
    });
  }

  // تحسين: إغلاق القائمة عند الضغط على رابط في الشاشات الصغيرة
  if (nav) {
    nav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ nav.classList.remove('show'); });
    });
  }
});