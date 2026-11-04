"""Gera assets/terminal.svg: janela de terminal com digitação animada (SMIL)."""
import sys
from html import escape

OUT = sys.argv[1]
W = 880
PAD = 26
CW = 9.0          # largura aproximada de um caractere (15px monospace)
LH = 25           # altura de linha
Y0 = 78           # baseline da primeira linha
CHAR_T = 0.06     # segundos por caractere digitado
FONT = "ui-monospace,SFMono-Regular,'JetBrains Mono','Cascadia Code',Menlo,Consolas,'Liberation Mono',monospace"

C = {
    "bg": "#0d1117", "bar": "#161b22", "border": "#30363d",
    "text": "#e6edf3", "dim": "#8b949e", "green": "#7ee787",
    "blue": "#79c0ff", "purple": "#d2a8ff", "orange": "#ffa657", "yellow": "#f2cc60",
}

PROMPT = [("johw", "green"), ("@", "dim"), ("intelbras", "green"), (":", "dim"), ("~", "blue"), ("$ ", "dim")]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)

# Cada item: ("cmd", texto) ou ("out", [(texto, cor), ...]) ou ("blank",) ou ("end",)
SCRIPT = [
    ("cmd", "whoami"),
    ("out", [("Johnatan Duarte ", "text"), ("(Johw)", "purple"), (" · Software Developer @ Intelbras · Palhoça/SC", "dim")]),
    ("blank",),
    ("cmd", "cat foco.txt"),
    ("out", [("→ ", "orange"), ("Controle de acesso e reconhecimento facial", "text")]),
    ("out", [("→ ", "orange"), ("IoT, ESP32 e automação com hardware", "text")]),
    ("out", [("→ ", "orange"), ("Cripto, privacidade e segurança · admin do Guia Anônima", "text")]),
    ("blank",),
    ("cmd", "ls ~/projetos --destaques"),
    ("out", [("IntelbrasModoOnlineElectron/  ", "blue"), ("FaceQualityAssurance/  ", "blue"), ("keystrokeDynamics2FA/", "blue")]),
    ("blank",),
    ("end",),
]


def tspans(parts):
    return "".join(f'<tspan fill="{C[c]}">{escape(t)}</tspan>' for t, c in parts)


def appear(t):
    return f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'


lines = len(SCRIPT)
H = Y0 + (lines - 1) * LH + 30
body = []
defs = []
t = 0.5
cmd_x = PAD + PROMPT_LEN * CW

for i, item in enumerate(SCRIPT):
    y = Y0 + i * LH
    kind = item[0]
    if kind == "blank":
        continue
    if kind in ("cmd", "end"):
        body.append(f'<text x="{PAD}" y="{y}" opacity="0">{tspans(PROMPT)}{appear(t)}</text>')
    if kind == "cmd":
        cmd = item[1]
        n = len(cmd)
        start = t + 0.35
        # revela caractere a caractere com valores discretos
        widths = ";".join(f"{k * CW + (CW if k else 0):.1f}" for k in range(n + 1))
        keytimes = ";".join(f"{k / (n + 1):.4f}" for k in range(n + 1))
        dur = (n + 1) * CHAR_T
        cid = f"c{i}"
        defs.append(
            f'<clipPath id="{cid}"><rect x="{cmd_x - 2}" y="{y - 18}" height="{LH}" width="0">'
            f'<animate attributeName="width" values="{widths}" keyTimes="{keytimes}" calcMode="discrete" '
            f'begin="{start:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(f'<text x="{cmd_x}" y="{y}" fill="{C["text"]}" clip-path="url(#{cid})">{escape(cmd)}</text>')
        # cursor acompanhando a digitação
        xs = ";".join(f"{cmd_x + k * CW:.1f}" for k in range(n + 1))
        body.append(
            f'<rect x="{cmd_x}" y="{y - 14}" width="{CW}" height="17" fill="{C["green"]}" opacity="0">'
            f'<set attributeName="opacity" to="0.85" begin="{t:.2f}s"/>'
            f'<animate attributeName="x" values="{xs}" keyTimes="{keytimes}" calcMode="discrete" begin="{start:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="visibility" to="hidden" begin="{start + dur + 0.15:.2f}s" fill="freeze"/></rect>'
        )
        t = start + dur + 0.35
    elif kind == "out":
        body.append(f'<text x="{PAD}" y="{y}" opacity="0">{tspans(item[1])}{appear(t)}</text>')
        t += 0.18
    elif kind == "end":
        body.append(
            f'<rect x="{cmd_x}" y="{y - 14}" width="{CW}" height="17" fill="{C["green"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0.85;0.85;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
            f'begin="{t:.2f}s" repeatCount="indefinite"/></rect>'
        )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: whoami — Johnatan Duarte (Johw), Software Developer na Intelbras">
<style>text{{font-family:{FONT};font-size:15px;white-space:pre}}</style>
<defs>{"".join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{C["bg"]}" stroke="{C["border"]}"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v26h-{W - 1}z" fill="{C["bar"]}" stroke="{C["border"]}"/>
<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
<text x="{W / 2}" y="24" text-anchor="middle" fill="{C["dim"]}" style="font-size:13px">johw@intelbras: ~</text>
{chr(10).join(body)}
</svg>
'''
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"ok {W}x{H}, animação termina em ~{t:.1f}s")
