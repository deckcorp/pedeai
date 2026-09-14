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
| `index.html` | Página de download |
| `app/index.html` | Versão web do app (a mesma que vai dentro do APK) |
| `guia.html`, `privacidade.html` | Guia visual e política de privacidade/termos |
| `version.json` | Lido pelo app instalado pra saber se tem atualização obrigatória |
| `pedeai-latest.apk` | APK da versão atual (o link fixo que o app e o site usam) |
| `CNAME`, `.nojekyll`, `.well-known/` | Configuração do GitHub Pages e do domínio |

## Versões

Cada versão do APK fica em **[Releases](https://github.com/deckcorp/pedeai/releases)**,
com o texto do que mudou. Os APKs numerados não ficam mais soltos no repositório.

Link fixo pra sempre baixar a versão mais nova, direto dos Releases:
`https://github.com/deckcorp/pedeai/releases/latest/download/pedeai-latest.apk`

## Como publicar uma versão nova

1. Gerar o APK e copiar pra `pedeai-latest.apk` na raiz.
2. Atualizar `version.json` (`version`, `versionCode`, `min`, `minVersionCode`, `notice`).
3. Atualizar a versão mostrada em `index.html` (botão e linha "APK Android · vX.Y.Z").
4. Commit e push na `main`. O GitHub Pages publica em ~1 minuto.
5. Criar o release com o APK anexado (o segundo arquivo é o link fixo):

   ```
   gh release create vX.Y.Z --title "PedeAí X.Y.Z" --notes "o que mudou" PedeAi-vX.Y.Z.apk pedeai-latest.apk
   ```

## Aviso

Este repositório é público **só porque o GitHub Pages grátis exige**.
Não deixe privado sem antes mover a hospedagem: o site, a versão web,
o download e a checagem de atualização dos apps instalados saem do ar.
Direitos reservados, veja `LICENSE`.
