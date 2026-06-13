/* sw.js — Compounding Stack service worker (PWA Phase 1)
 *
 * Strategy:
 *   /static/css|js/*  → cache-first  (versioned assets, long TTL ok)
 *   /static/icons/*   → cache-first
 *   /api/*            → network-only (no caching of API responses)
 *   everything else   → network-first (HTML pages stay fresh)
 */

const CACHE = 'csh-v1';

const PRECACHE = [
  '/static/css/tokens.css',
  '/static/css/app.css',
  '/static/js/sidebar.js',
  '/static/manifest.json',
];

// Install: pre-cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// Activate: remove old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: route by URL pattern
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls — never cache
  if (url.pathname.startsWith('/api/')) return;

  // Static assets — cache-first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE).then(cache => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML pages — network-first, fall back to cache
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
