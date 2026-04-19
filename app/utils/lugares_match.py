"""Coincidencia flexible origen/destino (viaje vs catalogo de tarifas)."""

from __future__ import annotations

import re

# Errores de captura frecuentes en demos / pruebas (ciudad base, minusculas).
_CIUDAD_TYPOS: dict[str, str] = {
    "vullahermosa": "villahermosa",
    "villahermoza": "villahermosa",
    "veracrus": "veracruz",
}


def _quitar_sufijos_estado(texto: str) -> str:
    s = (texto or "").strip().lower()
    s = re.sub(r",\s*ver\.?\s*$", "", s)
    s = re.sub(r",\s*tab\.?\s*$", "", s)
    s = re.sub(r",\s*tabasco\.?\s*$", "", s)
    s = re.sub(r"\s+ver\.?\s*$", "", s)
    s = re.sub(r"\s+tab\.?\s*$", "", s)
    return s.strip()


def _segmento_principal(texto: str) -> str:
    s = _quitar_sufijos_estado(texto)
    if not s:
        return ""
    return s.split(",")[0].strip()


def _palabras_sin_abrev_estado(parte: str) -> list[str]:
    """Quita al final tokens tipo Tab, Ver, NL (estado) si vienen sueltos."""
    raw = parte.replace(".", " ").split()
    stop = {"tab", "ver", "tabs", "nl", "cdmx", "mex"}
    while raw and raw[-1].lower() in stop:
        raw.pop()
    return raw


def ciudad_normalizada_para_tarifa(texto: str) -> str:
    """
    Clave comparable entre texto de viaje (con coma/estado) y fila de tarifa (corto).
    """
    seg = _segmento_principal(texto)
    if not seg:
        return ""
    words = _palabras_sin_abrev_estado(seg)
    if not words:
        return ""
    w0 = _CIUDAD_TYPOS.get(words[0].lower(), words[0].lower())
    rest = [w.lower() for w in words[1:]]
    return " ".join([w0] + rest).strip()


def lugares_equivalentes_para_tarifa(catalogo: str, solicitud: str) -> bool:
    """True si ciudad/ruta es la misma aunque difieran coma, estado o typo leve."""
    ca = ciudad_normalizada_para_tarifa(catalogo)
    so = ciudad_normalizada_para_tarifa(solicitud)
    if not ca or not so:
        return (catalogo or "").strip().lower() == (solicitud or "").strip().lower()
    return ca == so
