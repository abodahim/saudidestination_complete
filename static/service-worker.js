self.addEventListener('install', (e) => {
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  return clients.claim();
});
self.addEventListener('fetch', (e) => {
  // تمرير الطلبات بدون كاش معقّد
});
