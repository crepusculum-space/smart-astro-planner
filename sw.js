const CACHE_NAME = 'smart-astro-planner-v79';
const IMG_CACHE = 'sap-images';
const IMG_MAX = 80;
const IMG_HOSTS = ['alasky.cds.unistra.fr', 'alaskybis.cds.unistra.fr', 'upload.wikimedia.org'];
const ASSETS = ['manifest.json', 'icon-192.png', 'icon-512.png', 'help.html?v=5.8', 'catalog.json?v=5', 'astronomy.browser.min.js?v=2.1.19'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME && k !== IMG_CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (IMG_HOSTS.includes(url.hostname) && e.request.method === 'GET' && e.request.destination === 'image') {
    e.respondWith(imageFromCache(e.request));
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (e.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    e.respondWith(
      fetch(e.request).then(r => {
        const clone = r.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return r;
      }).catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
        const clone = resp.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return resp;
      }))
    );
  }
});

async function imageFromCache(request) {
  const cache = await caches.open(IMG_CACHE);
  const hit = await cache.match(request.url);
  if (hit) {
    // refresh recency: cache.keys() returns insertion order, so re-insert on use
    cache.put(request.url, hit.clone());
    return hit;
  }
  try {
    const resp = await fetch(request.url, { mode: 'cors' });
    if (resp.ok) {
      await cache.put(request.url, resp.clone());
      const keys = await cache.keys();
      for (let i = 0; i < keys.length - IMG_MAX; i++) await cache.delete(keys[i]);
    }
    return resp;
  } catch (err) {
    return fetch(request);
  }
}
