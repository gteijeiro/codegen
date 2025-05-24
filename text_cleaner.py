# text_cleaner.py
"""
Funciones reutilizables para “sanear” la respuesta del modelo.
Añade o registra más pasos sin tocar el front-end.

Uso rápido:
    from text_cleaner import clean
    texto_limpio = clean(texto_bruto)
"""

import re
from typing import Callable, List

# ── patrones base ──────────────────────────────────────────
THINK_RE = re.compile(r"<think>.*?</think>", re.I | re.S)              # ignora mayúsculas
CODE_RE  = re.compile(r"```(?:[^\n]*\n)?(.*?)```", re.S)               # 1er bloque ```

# ── pasos de limpieza ──────────────────────────────────────
def remove_think(text: str) -> str:
    """Elimina cualquier bloque <think> … </think>."""
    return THINK_RE.sub("", text)

def extract_first_code(text: str) -> str:
    """Devuelve el primer bloque ```código``` o el texto tal cual si no hay."""
    m = CODE_RE.search(text)
    return m.group(1).rstrip() if m else text.rstrip()

# pipeline editable
PIPELINE: List[Callable[[str], str]] = [
    remove_think,
    extract_first_code,
]

def clean(text: str) -> str:
    """Aplica, en orden, todas las funciones declaradas en PIPELINE."""
    for step in PIPELINE:
        text = step(text)
    return text

# api para extender sin abrir este archivo:
def register(step: Callable[[str], str], position: int | None = None) -> None:
    """
    Agrega un nuevo paso al pipeline.
    position=None lo añade al final; de lo contrario, lo inserta donde indiques.
    """
    if position is None:
        PIPELINE.append(step)
    else:
        PIPELINE.insert(position, step)
