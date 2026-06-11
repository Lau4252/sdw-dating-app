const CACHE_NAME = 'stipconnect-v1';
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/css/custom.css',
    '/static/images/icon-192.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Cache-First für statische Assets
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request).then(cached => {
                return cached || fetch(request).then(response => {
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, response.clone());
                        return response;
                    });
                });
            })
        );
        return;
    }

    // Network-First für HTML-Seiten
    if (request.mode === 'navigate' || request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(request).then(response => {
                return caches.open(CACHE_NAME).then(cache => {
                    cache.put(request, response.clone());
                    return response;
                });
            }).catch(() => {
                return caches.match(request).then(cached => {
                    return cached || caches.match('/');
                });
            })
        );
        return;
    }

    // Standard: Netzwerk mit Cache-Fallback
    event.respondWith(
        fetch(request).catch(() => {
            return caches.match(request);
        })
    );
});
