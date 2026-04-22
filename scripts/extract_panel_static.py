"""
Extrae CSS y JS del panel desde app/web.py hacia app/static/panel/ y deja un _UI_TEMPLATE liviano.

Ejecutar una vez desde la raíz del repo:
  python scripts/extract_panel_static.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_PY = ROOT / "app" / "web.py"
CSS_OUT = ROOT / "app" / "static" / "panel" / "panel.css"
JS_OUT = ROOT / "app" / "static" / "panel" / "panel.js"


def main() -> None:
    text = WEB_PY.read_text(encoding="utf-8")
    m = re.search(
        r'_UI_TEMPLATE = """(.+?)"""\n\n\ndef _render_ui',
        text,
        re.DOTALL,
    )
    if not m:
        raise SystemExit("No se encontro _UI_TEMPLATE en app/web.py")
    tmpl = m.group(1)
    i_style = tmpl.find("<style>")
    j_style = tmpl.find("</style>", i_style)
    i_script = tmpl.find("<script>")
    j_script = tmpl.find("</script>", i_script)
    if min(i_style, j_style, i_script, j_script) < 0:
        raise SystemExit("Marcadores <style> o <script> no encontrados (¿ya extraido?)")

    css = tmpl[i_style + len("<style>") : j_style].strip("\n")
    js = tmpl[i_script + len("<script>") : j_script].strip("\n")

    old_hdr = '    const API_BASE = "/api/v1";\n    const API_KEY = __API_KEY__;'
    new_hdr = """    const panelBoot = window.__SIFE_PANEL_BOOT__ || {};
    const API_BASE = panelBoot.apiBase || "/api/v1";
    const API_KEY = panelBoot.apiKey || "";"""
    if old_hdr not in js:
        if "const API_BASE" in js and "__API_KEY__" in js:
            raise SystemExit("Cabecera API_BASE/API_KEY cambio; ajustar script extract_panel_static.py")
        raise SystemExit("No se encontro cabecera API_BASE/API_KEY en el JS extraido")
    js = js.replace(old_hdr, new_hdr, 1)

    CSS_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSS_OUT.write_text(css + "\n", encoding="utf-8")
    JS_OUT.write_text(js + "\n", encoding="utf-8")

    before = tmpl[:i_style].rstrip()
    after_style = tmpl[j_style + len("</style>") : i_script]
    after_script = tmpl[j_script + len("</script>") :]

    new_tmpl = (
        before
        + "\n  <link rel=\"stylesheet\" href=\"/static/panel/panel.css\" />"
        + after_style
        + "\n  <script>\n    window.__SIFE_PANEL_BOOT__ = { apiBase: \"/api/v1\", apiKey: __API_KEY__ };\n  </script>\n"
        + '  <script src="/static/panel/panel.js" defer></script>'
        + after_script
    )

    new_text = text[: m.start(1)] + new_tmpl + text[m.end(1) :]
    WEB_PY.write_text(new_text, encoding="utf-8")
    print("OK:", CSS_OUT.relative_to(ROOT), JS_OUT.relative_to(ROOT), "web.py actualizado.")


if __name__ == "__main__":
    main()
