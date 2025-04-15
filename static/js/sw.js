const CACHE_NAME = 'my-cache-v1';
const urlsToCache = [
    '/',  // Home page
    '/static/js/script.js', // Your main JS file
    '/static/css/style.css', // Your main CSS file
    '/static/images/icon.png', // Your project icon or any image you want to cache
    // Add other files to cache as needed
];

// Install event - called when the service worker is first installed
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Activate event - called after the service worker is installed
self.addEventListener('activate', (event) => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (!cacheWhitelist.includes(cacheName)) {
                        // Delete outdated cache
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - intercepting network requests to serve cached content
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                // If we have a cached response, return it, else fetch from the network
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request);
            })
    );
});
