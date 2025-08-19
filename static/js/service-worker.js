// static/js/service-worker.js
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// لا نعمل كاش الآن لتبسيط الأمور (تقدر تطور لاحقًا)
self.addEventListener('fetch', (event) => {
  // تمرير الطلبات بدون تدخل
});
