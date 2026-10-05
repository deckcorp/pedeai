/* PedeAí — aposentadoria do service worker antigo da raiz.
   Quando o app morava em "/", ele registrava este arquivo com escopo "/". Hoje o app fica em
   /app/ (com o próprio /app/sw.js) e a raiz é só a página inicial, que não usa service worker.
   Navegadores que ainda têm o registro antigo buscam este arquivo ao checar atualização:
   esta versão não intercepta nada, apaga só o cache que era dele e se desregistra.
   NÃO apagar este arquivo: sem ele (404) o registro antigo continuaria vivo nesses navegadores. */
var OLD_ROOT_CACHES = ["pedeai-v4-7"];
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(
    Promise.all(OLD_ROOT_CACHES.map(function (k) { return caches.delete(k).catch(function () {}); }))
      .then(function () { return self.registration.unregister(); })
      .catch(function () {})
  );
});
