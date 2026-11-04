"""Valida as imagens do README antes que quebrem no perfil.

Uso: python3 scripts/check_readme.py [README.md]

- srcset não pode ter vírgula literal (o GitHub corta a URL nela; use %2C)
- imagens relativas precisam existir no repositório
- imagens externas precisam responder 200 com content-type de imagem
  (as da branch `output`, geradas pela Action da cobrinha, só geram aviso)
"""
import re
import sys
import urllib.request
from pathlib import Path

readme = Path(sys.argv[1] if len(sys.argv) > 1 else "README.md")
root = Path(__file__).resolve().parent.parent
html = readme.read_text(encoding="utf-8")
errors, warnings = [], []

srcsets = re.findall(r'srcset="([^"]*)"', html)
srcs = re.findall(r'<img[^>]*\ssrc="([^"]*)"', html)

for s in srcsets:
    if "," in s:
        errors.append(f"srcset com vírgula literal (troque por %2C): {s}")

for url in dict.fromkeys(srcsets + srcs):
    if not url.startswith("http"):
        if not (root / url.lstrip("./")).is_file():
            errors.append(f"arquivo local não existe: {url}")
        continue
    if "," in url:
        continue  # já reportado acima
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "readme-check"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = r.headers.get("content-type", "")
            if r.status != 200 or not ctype.startswith("image/"):
                errors.append(f"{r.status} {ctype}: {url}")
    except Exception as e:  # noqa: BLE001
        target = warnings if "/output/" in url else errors
        target.append(f"{e}: {url}")

for w in warnings:
    print(f"AVISO: {w}")
for e in errors:
    print(f"ERRO: {e}")
print(f"{len(srcsets) + len(srcs)} imagens verificadas, {len(errors)} erro(s), {len(warnings)} aviso(s)")
sys.exit(1 if errors else 0)
