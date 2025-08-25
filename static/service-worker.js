// تخزين مؤقت بسيط
const CACHE = 'sd-cache-v2'; // غيّر الرقم لتحديث الكاش
const ASSETS = [
  '/', '/manifest.webmanifest',
  '/static/styles.css', '/static/script.js',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k!==CACHE).map(k => caches.delete(k)))
    )
  );
});
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});