# PedeAí

Comanda digital pra bar: anota pedidos por mesa, soma e fecha a conta.
Funciona sem internet e vários celulares do mesmo bar sincronizam entre si
(caixa, garçom e cozinha).

Site e download: **https://pedeai.deckcorp.com.br**

## O que tem neste repositório

Só a vitrine publicada no GitHub Pages. O código-fonte do app Android
(projeto Capacitor) e do servidor **não** está aqui.

| Arquivo | Pra que serve |
|---|---|
| `index.html` | Página inicial (landing): apresenta o produto e leva ao teste e à instalação |
| `app/index.html` | Versão web do app (a mesma que vai dentro do APK) |
| `guia.html`, `privacidade.html` | Guia visual e política de privacidade/termos |
| `version.json` | **Fonte da versão.** Lido pelo app instalado (atualização obrigatória) e pela página inicial (botão e número da versão do Android) |
| `pedeai-X.Y.Z.apk` | APK numerado da versão atual. É o arquivo que o `apkUrl` do `version.json` aponta |
| `pedeai-latest.apk` | APK da versão atual (o link fixo que o app e o site usam) |
| `og-image.jpg`, `fonts/` | Imagem que aparece ao compartilhar o link e as fontes da página inicial (hospedadas aqui, sem Google Fonts) |
| `tools/conferir-release.py` | Conferência automática antes de publicar |
| `CNAME`, `.nojekyll`, `.well-known/` | Configuração do GitHub Pages e do domínio |

## Versões

Cada versão do APK fica em **[Releases](https://github.com/deckcorp/pedeai/releases)**,
com o texto do que mudou. Na raiz só precisam ficar o APK numerado da versão atual
e o `pedeai-latest.apk` (os de versões antigas que ainda estão aqui podem sair:
o app obriga a atualizar e eles continuam nos Releases).

Link fixo pra sempre baixar a versão mais nova, direto dos Releases:
`https://github.com/deckcorp/pedeai/releases/latest/download/pedeai-latest.apk`

## Como publicar uma versão nova

A ordem importa. O app instalado lê o `version.json` e **obriga** a atualizar;
se ele apontar pra um APK que ainda não está no ar, o cliente fica sem conseguir atualizar.
Por isso o `version.json` é sempre o **último** a mudar.

No projeto do app (`~/claude-projetos/pedeai`):

1. Subir a versão nos três lugares: `package.json`, `android/app/build.gradle`
   (`versionName` e `versionCode`) e `www/index.html` (`VERSION` e `VERSION_CODE`).
   Copiar `www/index.html` por cima do `index.html` da raiz.
2. `npm test` — tem que passar inteiro (confere versão igual nos três lugares,
   biblioteca de QR dentro de `www/` e Android sem plugin sobrando).
3. `./build-apk.sh` — gera `dist/PedeAi-vX.Y.Z.apk` assinado e confere o pacote.

Neste repositório (o site):

4. Copiar o APK pra raiz duas vezes: `pedeai-X.Y.Z.apk` e `pedeai-latest.apk`.
5. Copiar a versão web: `www/index.html` → `app/index.html` (e `www/vendor/` → `app/vendor/`,
   `www/sw.js` → `app/sw.js` se mudaram).
6. **Por último**, atualizar o `version.json` (`version`, `versionCode`, `min`, `minVersionCode`,
   `apkUrl`, `notice`). A página inicial lê esse arquivo sozinha: não precisa editar o `index.html`.
7. Conferir tudo de uma vez:

   ```
   python3 tools/conferir-release.py
   ```

   Ele confere: APK do `version.json` existe e é a versão certa, assinatura do APK bate com
   `.well-known/assetlinks.json` (senão o link do convite não abre no app), biblioteca de QR
   dentro do APK, `app/` na mesma versão e página inicial sem versão escrita à mão.
   Só publique com "Tudo certo para publicar". Se só a página mudou (sem app novo), use
   `python3 tools/conferir-release.py --so-pagina`.
8. Um commit só com APK + `app/` + `version.json`, e push na `main`. O GitHub Pages publica em
   ~1 minuto e guarda as páginas por até 10 minutos.
9. Conferir no ar: abrir `https://pedeai.deckcorp.com.br/version.json`, baixar o APK pelo botão
   da página e ver se a seção Instalar mostra a versão nova.
10. Criar o release com o APK anexado (o segundo arquivo é o link fixo):

   ```
   gh release create vX.Y.Z --title "PedeAí X.Y.Z" --notes "o que mudou" PedeAi-vX.Y.Z.apk pedeai-latest.apk
   ```

O painel (`/api/pedeai/version`) é só reserva: o app usa o `version.json` do site e só consulta
o painel quando o site não responde. Mantenha os dois iguais.

## Arquivos legados que precisam ficar

- `sw.js` (raiz): não é mais usado por nenhuma página. Ele existe pra desligar o service worker
  antigo em navegadores que instalaram o app quando ele morava na raiz. **Não apagar.**
- `manifest.webmanifest` (raiz): a página inicial aponta pra ele; quem "instala" o site pelo
  navegador cai direto em `/app/`.

## Aviso

Este repositório é público **só porque o GitHub Pages grátis exige**.
Não deixe privado sem antes mover a hospedagem: o site, a versão web,
o download e a checagem de atualização dos apps instalados saem do ar.
Direitos reservados, veja `LICENSE`.
