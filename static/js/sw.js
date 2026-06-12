// StipConnect Service Worker — Offline-First PWA v3

const CACHE_NAME = 'stipconnect-v3';
const OFFLINE_PAGE = '/';

// Core assets: everything needed for the app shell to render without network
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/css/custom.css',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png',
    '/static/images/icon-maskable-192.png',
    '/static/images/icon-maskable-512.png',
    '/browse/',
    '/matches/',
    '/datenschutz/',
];

// ── INSTALL ──────────────────────────────────────────────
self.addEventListener('install', event => {
    console.log('[SW] installing v3…');
    event.waitUntil(
        caches.open(CACHE_NAME).then(async cache => {
            // Precache the static shell assets
            for (const url of STATIC_ASSETS) {
                try {
                    await cache.add(new Request(url, { cache: 'reload' }));
                } catch (err) {
                    console.warn('[SW] precache failed for', url, err.message);
                }
            }
        })
    );
    self.skipWaiting();
});

// ── ACTIVATE ─────────────────────────────────────────────
self.addEventListener('activate', event => {
    console.log('[SW] activating v3…');
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// ── FETCH ────────────────────────────────────────────────
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip chrome-extension:// and other non-http(s) requests
    if (!url.protocol.startsWith('http')) return;

    // 1) Cache-First für statische Assets (/static/)
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request).then(cached => {
                if (cached) return cached;
                return fetch(request).then(response => {
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, response.clone());
                        return response;
                    });
                });
            })
        );
        return;
    }

    // 2) Stale-While-Revalidate für HTML-Seiten (Navigation)
    if (request.mode === 'navigate' || request.destination === 'document') {
        event.respondWith(
            caches.match(request).then(cachedResponse => {
                const fetchPromise = fetch(request).then(networkResponse => {
                    if (networkResponse && networkResponse.ok) {
                        const clone = networkResponse.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return networkResponse;
                }).catch(() => cachedResponse);

                return cachedResponse || fetchPromise;
            })
        );
        return;
    }

    // 3) Network-First für alles andere (API, JSON, etc.)
    event.respondWith(
        fetch(request).then(response => {
            if (response && response.ok) {
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
            }
            return response;
        }).catch(() => {
            return caches.match(request).then(cached => {
                return cached || caches.match(OFFLINE_PAGE);
            });
        })
    );
});

// ── BACKGROUND SYNC (for likes/swipes) ───────────────────
self.addEventListener('sync', event => {
    if (event.tag === 'sync-swipes') {
        event.waitUntil(syncPendingSwipes());
    }
});

async function syncPendingSwipes() {
    // Placeholder: replay queued swipe actions from IndexedDB
    console.log('[SW] background sync: sync-swipes');
}

// ── PUSH NOTIFICATIONS ───────────────────────────────────
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'StipConnect';
    const options = {
        body: data.body || 'Neues Match!',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/icon-maskable-192.png',
        tag: data.tag || 'default',
        data: data,
        requireInteraction: true,
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    const urlToOpen = event.notification.data?.url || '/browse/';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            for (const client of windowClients) {
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) return clients.openWindow(urlToOpen);
        })
    );
});

// ── MESSAGE HANDLING (from client JS) ────────────────────
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
