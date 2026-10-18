const CACHE_NAME = 'rb-agent-os-v1.0.0';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/static/css/style.css',
  '/static/css/reactor.css',
  '/static/js/app.js',
  '/static/js/reactor.js',
  '/static/js/chat.js',
  '/static/js/voice.js',
  '/static/js/settings.js',
  '/static/js/pwa.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip caching API requests - always network only
  if (url.pathname.startsWith('/api')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({
            status: "offline",
            error: "Device is currently offline. Local cache active."
          }),
          { headers: { "Content-Type": "application/json" } }
        );
      })
    );
    return;
  }

  // Network-first with cache fallback for HTML and assets
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (event.request.headers.get('accept').includes('text/html')) {
            return caches.match('/');
          }
        });
      })
  );
});
