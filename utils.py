#Funciones genéricas (sanitize, substitute, cargar archivo).
from pathlib import Path
import re
import streamlit as st

ILLEGAL = set('<>:"/\\|?*%')
PLACE_RE = re.compile(r"<%([^%>]+)%>")

# ---------- funciones utilitarias ------------------
def substitute(txt: str, mp: dict) -> str:
    return PLACE_RE.sub(lambda m: mp.get(m.group(1).lower(), m.group(0)), txt)

sanitize = lambda s: "".join(c for c in s if c not in ILLEGAL)

def load_file_from_secrets(section: str, default: str) -> Path:
    return Path(st.secrets.get(section, {}).get("path", default))
