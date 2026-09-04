/* Offline-capable: the app still opens with no signal at all — she may well be
   standing in a room full of plants with her phone on airplane mode. The shell
   is fetched fresh when there IS a signal and falls back to the cached copy
   when there is not (see the fetch handler); icons and fonts stay cache-first.
   Bump CACHE when you want to evict everything a device has cached. */
const CACHE = "potting-bench-v46";
const SHELL = ["./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

/* The app shell is NETWORK-first, everything else cache-first.

   It used to be cache-first for everything, which quietly froze the app: once
   a device had the HTML in the cache it was served from there on every visit
   for ever, so a deploy only reached that device if CACHE happened to change.
   Twenty-five builds shipped under one cache name, and phones and laptops that
   had loaded the site once were still running the build from the day they
   first opened it — while the site itself was up to date.

   Network-first costs one request the browser would make anyway, and the catch
   below still serves the cached shell when there is no signal, which is the
   case this worker exists for. */
const isShell = req => {
  if (req.mode === "navigate") return true;
  const u = new URL(req.url);
  return u.origin === self.location.origin &&
         (u.pathname === "/" || u.pathname.endsWith("/index.html"));
};

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  if (isShell(e.request)) {
    e.respondWith(
      fetch(e.request).then(res => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match(e.request).then(hit => hit || caches.match("./index.html")))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      /* keep the Google Fonts files once fetched, so type survives offline too */
      if (res.ok && (e.request.url.startsWith(self.location.origin) ||
                     e.request.url.includes("fonts.g"))) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match("./index.html")))
  );
});
