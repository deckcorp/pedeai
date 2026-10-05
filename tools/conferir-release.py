#!/usr/bin/env python3
"""Confere se o site está coerente ANTES de publicar uma versão do PedeAí.

Uso:  python3 tools/conferir-release.py              (antes de publicar uma versão nova do app)
      python3 tools/conferir-release.py --so-pagina  (só mudou a página; o APK é o que já está no ar:
                                                      defeitos de dentro do APK viram aviso)
Sai com erro (código 1) se achar algo que deixaria cliente sem conseguir atualizar,
baixando a versão errada, ou com o link de convite sem abrir no app.
"""
import glob, hashlib, json, os, re, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
erros, avisos = [], []
SO_PAGINA = "--so-pagina" in sys.argv

def ok(msg): print("  ok   ", msg)
def erro(msg): erros.append(msg); print("  ERRO ", msg)
def aviso(msg): avisos.append(msg); print("  aviso", msg)

def ferramenta(nome):
    base = os.environ.get("ANDROID_HOME", "/opt/homebrew/share/android-commandlinetools")
    achados = sorted(glob.glob(os.path.join(base, "build-tools", "*", nome)))
    return achados[-1] if achados else None

def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()

print("1. version.json")
try:
    v = json.load(open("version.json", encoding="utf-8"))
except Exception as e:
    erro(f"version.json inválido: {e}"); sys.exit(1)
for campo in ("version", "min", "versionCode", "minVersionCode", "apkUrl"):
    if campo not in v: erro(f"version.json sem o campo {campo}")
versao, codigo = str(v.get("version", "")), int(v.get("versionCode", 0) or 0)
if not re.fullmatch(r"\d+(\.\d+){1,3}", versao): erro(f"versão estranha: {versao!r}")
else: ok(f"versão {versao} (código {codigo}), mínima {v.get('min')} (código {v.get('minVersionCode')})")
if int(v.get("minVersionCode", 0) or 0) > codigo: erro("minVersionCode maior que versionCode: ninguém conseguiria ficar em dia")

print("2. APK apontado pelo version.json")
url = str(v.get("apkUrl", ""))
apk = url.rsplit("/", 1)[-1]
if not url.startswith("https://pedeai.deckcorp.com.br/"): erro(f"apkUrl fora do site: {url}")
if not os.path.isfile(apk) or os.path.getsize(apk) < 1_000_000:
    erro(f"{apk} não existe aqui (ou está vazio). Quem tem o app instalado ficaria preso na tela de atualização.")
else:
    ok(f"{apk} existe ({os.path.getsize(apk) // 1024} KB)")
    if not os.path.isfile("pedeai-latest.apk"): erro("pedeai-latest.apk não existe")
    elif sha256("pedeai-latest.apk") != sha256(apk): erro(f"pedeai-latest.apk é diferente de {apk}")
    else: ok("pedeai-latest.apk é o mesmo arquivo")
    aapt, apksigner = ferramenta("aapt"), ferramenta("apksigner")
    if not aapt or not apksigner:
        aviso("ferramentas do Android (aapt/apksigner) não encontradas: versão e assinatura do APK não foram conferidas")
    else:
        selo = subprocess.run([aapt, "dump", "badging", apk], capture_output=True, text=True).stdout
        m = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", selo)
        if not m: erro("não consegui ler a versão de dentro do APK")
        else:
            pacote, cod_apk, nome_apk = m.group(1), int(m.group(2)), m.group(3)
            if pacote != "com.deckcorp.pedeai": erro(f"pacote do APK é {pacote} (build de teste?)")
            if nome_apk != versao or cod_apk != codigo: erro(f"APK é {nome_apk} ({cod_apk}), version.json diz {versao} ({codigo})")
            else: ok(f"APK é mesmo a versão {nome_apk} ({cod_apk}), pacote {pacote}")
        cert = subprocess.run([apksigner, "verify", "--print-certs", apk], capture_output=True, text=True).stdout
        m = re.search(r"SHA-256 digest: ([0-9a-f]{64})", cert)
        if not m: erro("APK sem assinatura válida")
        else:
            digital = ":".join(m.group(1).upper()[i:i + 2] for i in range(0, 64, 2))
            try:
                alvo = json.load(open(".well-known/assetlinks.json"))[0]["target"]
                if alvo.get("package_name") != "com.deckcorp.pedeai": erro("assetlinks.json com package_name errado")
                if digital not in alvo.get("sha256_cert_fingerprints", []):
                    erro("assetlinks.json não tem a assinatura deste APK: o link do convite não abriria no app")
                else: ok("assinatura do APK confere com .well-known/assetlinks.json")
            except Exception as e:
                erro(f".well-known/assetlinks.json inválido: {e}")
        conteudo = subprocess.run(["unzip", "-l", apk], capture_output=True, text=True).stdout
        html_apk = subprocess.run(["unzip", "-p", apk, "assets/public/index.html"], capture_output=True, text=True).stdout
        for script in re.findall(r'<script src="([^"]+)"', html_apk):
            if script.startswith("http"): continue
            if f"assets/public/{script}" not in conteudo:
                (aviso if SO_PAGINA else erro)(f"o APK carrega {script}, mas o arquivo não está dentro dele")
            else: ok(f"{script} está dentro do APK")

print("3. Versão web (app/)")
web = open("app/index.html", encoding="utf-8").read()
m, c = re.search(r'VERSION = "([^"]+)"', web), re.search(r"var VERSION_CODE = (\d+);", web)
if not m or not c: erro("não achei VERSION/VERSION_CODE em app/index.html")
elif m.group(1) != versao or int(c.group(1)) != codigo:
    erro(f"app/index.html é {m.group(1)} ({c.group(1)}), version.json diz {versao} ({codigo})")
else: ok(f"app/index.html é a versão {versao} ({codigo})")
for script in re.findall(r'<script src="([^"]+)"', web):
    if not script.startswith("http") and not os.path.isfile(os.path.join("app", script)): erro(f"app/{script} não existe")

print("4. Página inicial")
pagina = open("index.html", encoding="utf-8").read()
fixas = set(re.findall(r"\b\d+\.\d+\.\d+\b", re.sub(r"<svg.*?</svg>", "", pagina, flags=re.S)))
if fixas: aviso(f"index.html tem número de versão escrito à mão: {sorted(fixas)} (ela deve ler do version.json)")
else: ok("index.html não tem versão escrita à mão (lê do version.json)")
for arq in ("og-image.jpg", "icon.svg", "guia.html", "privacidade.html", "sw.js", ".well-known/assetlinks.json", "CNAME", ".nojekyll"):
    if not os.path.isfile(arq): erro(f"falta o arquivo {arq}")
for ref in set(re.findall(r'(?:href|src)="((?!https?:|mailto:|#)[^"#?]+)', pagina)):
    if not os.path.exists(ref): erro(f"index.html aponta para {ref}, que não existe")

print()
if erros:
    print(f"NÃO PUBLICAR: {len(erros)} erro(s).")
    sys.exit(1)
print("Tudo certo para publicar." + (f" ({len(avisos)} aviso(s) acima.)" if avisos else ""))
