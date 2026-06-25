/* sw.js — Compounding Stack service worker (PWA Phase 2)
 *
 * Strategy:
 *   /static/*  → network-first  (fresh assets win; cache is offline fallback only)
 *   /api/*     → bypass (no caching of API responses)
 *   HTML pages → network-first  (pages stay fresh; cache fallback offline)
 *
 * WHY network-first for /static (was cache-first in Phase 1):
 *   Phase 1 served /static/css|js cache-first under a fixed cache name ('csh-v1').
 *   Because the cache name never changed between deploys and the SW script itself
 *   never changed, the browser never re-installed the SW and kept serving STALE
 *   css/js forever — a plain "Redeploy" + browser "cache clear" did NOT update the
 *   page, because the Service Worker Cache Storage is separate from the HTTP cache.
 *   This made every design/CSS change invisible to returning (and PWA-installed)
 *   users. Network-first guarantees a deploy is reflected on the next reload while
 *   still working offline via the cache fallback. (common-adapter fix — all demos)
 *
 * NOTE: bump CACHE on any change to this file so activate() purges the prior cache.
 */

const CACHE = 'csh-v2';

const PRECACHE = [
  '/static/css/tokens.css',
  '/static/css/app.css',
  '/static/js/sidebar.js',
  '/static/manifest.json',
];

// Install: pre-cache core static assets (fetched fresh into the new cache).
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// Activate: delete every cache that is not the current one (purges stale 'csh-v1').
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// network-first: try the network, update the cache on success, fall back to cache
// (offline) on failure. Used for both /static and HTML so deploys always win.
function networkFirst(request) {
  return fetch(request)
    .then(response => {
      if (response && response.ok) {
        const clone = response.clone();
        caches.open(CACHE).then(cache => cache.put(request, clone));
      }
      return response;
    })
    .catch(() => caches.match(request));
}

// Fetch: route by URL pattern.
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls — never cache, let them hit the network directly.
  if (url.pathname.startsWith('/api/')) return;

  // Static assets + HTML pages — network-first with offline cache fallback.
  event.respondWith(networkFirst(request));
});
