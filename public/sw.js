const VERSION='campus-palette-v1';
const ROOT=new URL('./',self.location.href);
self.addEventListener('install',e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(['./','./manifest.webmanifest','./icon-192.png','./icon-512.png'])).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('campus-palette-')&&k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
// Network first, including official-data JSON: updates arrive without reinstalling.
// Cache only this application's scope. External university PDFs are never cached.
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==ROOT.origin||!u.pathname.startsWith(ROOT.pathname))return;
 e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();e.waitUntil(caches.open(VERSION).then(c=>c.put(e.request,copy)));}return r;}).catch(async()=>{const cached=await caches.match(e.request);if(cached)return cached;if(e.request.mode==='navigate'){const shell=await caches.match(ROOT.href);if(shell)return shell;}return new Response('オフラインで読み込めるデータがありません。',{status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}});}));});
