self.addEventListener('install', (e) => self.skipWaiting());
self.addEventListener('activate', (e) => clients.claim());
self.addEventListener('fetch', (e) => {
  // تمرير الطلبات كما هي — يمكن إضافة كاش لاحقًا
});