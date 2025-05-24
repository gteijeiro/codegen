import json
import re
import streamlit as st
from pathlib import Path

from streamlit_chat import message
from utils import substitute, sanitize, load_file_from_secrets, PLACE_RE, ILLEGAL
from contants import API_DIR, STATIC_DIR
# ── adaptadores de modelos (dos implementaciones) ──
from model_client import ModelClient as ClassicClient
from model_client_azure_preview import ModelClient as PreviewClient
from text_cleaner import clean as clean_api            # limpieza de respuestas

# ========= Mapear modelos declarados en secrets =========
MODELS_CFG = {
    section: cfg for section, cfg in st.secrets.items()
    if section.startswith("model_")
}
if not MODELS_CFG:
    st.error("No se encontró ningún bloque [model_*] en secrets.toml.")
    st.stop()




# Directrices externas
DIR_PATH = load_file_from_secrets("directives", "directives.txt")
BASE_DIRECTIVES = DIR_PATH.read_text("utf-8") if DIR_PATH.exists() else ""

# Variables JSON por defecto
VARS_PATH = load_file_from_secrets("varsfile", "variables.json")
vars_json_default = VARS_PATH.read_text("utf-8") if VARS_PATH.exists() else "{}"

# ---------- selector de modelo / versión ------------
sidebar_model_keys = list(MODELS_CFG.keys())
default_model_key  = st.session_state.get("model_key", sidebar_model_keys[0])

with st.sidebar:
    model_key = st.selectbox(
        "Modelo disponible",
        sidebar_model_keys,
        index=sidebar_model_keys.index(default_model_key)
    )
    st.session_state["model_key"] = model_key
    st.caption(
        f"{MODELS_CFG[model_key].get('deployment', MODELS_CFG[model_key].get('model_name'))} "
        f"· {MODELS_CFG[model_key].get('api_version','')}"
    )

# ---------- cargador del cliente (cache) -------------
@st.cache_resource
def load_model(cfg_key: str):
    cfg = MODELS_CFG[cfg_key]
    provider = cfg.get("provider", "2024-12-01-preview")

    if provider == "2024-12-01-preview":
        return PreviewClient(
            endpoint    = cfg["endpoint"],
            api_key     = cfg["api_key"],
            deployment  = cfg["deployment"],
            api_version = cfg.get("api_version", "2024-12-01-preview"),
        )
    elif provider == "azure_deepseek":
        return ClassicClient(provider, cfg)
    else:
        st.error(f"Proveedor no soportado: {provider}")
        st.stop()

client = load_model(model_key)

# ---------- UI principal -----------------------------
st.title("💬 Generador de código")

# === SIDEBAR (parámetros adicionales) ===============
with st.sidebar:
    temp = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.05)

    # Único cuadro Entity
    entity = sanitize(st.text_input("Entity", st.session_state.get("entity", ""),
                                    key="entity_input"))
    st.session_state["entity"] = entity

    vars_text = st.text_area(
        "Variables JSON (reemplazan <%Clave%>)",
        st.session_state.get("vars_json", vars_json_default),
        height=220
    )
    st.session_state["vars_json"] = vars_text

    # Parseo del JSON
    try:
        data = json.loads(vars_text or "{}")
        variables         = {k.lower(): str(v) for k, v in data.get("variables", {}).items()}
        global_prompt_cfg = data.get("globalPrompt", "")
        template_prompts  = data.get("templatePrompts", {})
    except Exception as e:
        st.error(f"JSON inválido: {e}")
        st.stop()

    # si JSON trae "entity" y el cuadro está vacío → sincroniza (sin crear otro widget)
    if not entity and variables.get("entity"):
        entity = sanitize(variables["entity"])
        st.session_state["entity"] = entity

    variables["entity"] = entity         # asegura que esté en dict

    # Prompt global
    global_prompt = st.text_area(
        "Prompt global (pre-antepuesto a cada template)",
        st.session_state.get("global_prompt", global_prompt_cfg),
        height=100
    )
    st.session_state["global_prompt"] = global_prompt

    # Prompts por template API
    st.header("Prompts por template API")
    api_templates = sorted(API_DIR.glob("*.txt"))
    if "prompt_map" not in st.session_state:
        st.session_state["prompt_map"] = {
            tpl.name: template_prompts.get(tpl.name, global_prompt)
            for tpl in api_templates
        }

    for tpl in api_templates:
        with st.expander(tpl.name):
            key = f"prompt_{tpl.name}_{model_key}"
            st.session_state["prompt_map"][tpl.name] = st.text_area(
                "Prompt", st.session_state["prompt_map"][tpl.name],
                key=key, height=120
            )

    # Carpeta de salida
    out_dir = Path(st.text_input("📁 Carpeta salida", "generated")).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    st.caption(out_dir.resolve())

    col1, col2 = st.columns(2)
    with col1: gen_click = st.button("🚀 Generar código")
    with col2:
        if st.button("🗑️ Reiniciar"):
            st.session_state.clear(); st.rerun()

# === HISTORIAL ======================================
if "hist" not in st.session_state:
    st.session_state["hist"] = []
for i, (role, txt) in enumerate(st.session_state["hist"]):
    message(txt, is_user=(role == "user"), key=f"msg_{i}")

# === GENERACIÓN =====================================
if gen_click:
    try:
        var_map = {k.lower(): str(v) for k, v in json.loads(vars_text or "{}").items()}
    except Exception as e:
        st.error(f"JSON inválido: {e}"); st.stop()

    var_map["entity"] = entity
    st.session_state["var_map"] = var_map

    # Templates API
    api_results = []
    for tpl in api_templates:
        pr_global = st.session_state["global_prompt"].strip()
        pr_file   = st.session_state["prompt_map"][tpl.name].strip()
        prompt_final = f"{pr_global}\n{pr_file}".strip()

        if not prompt_final:
            st.warning(f"{tpl.name} sin prompt — omitido."); continue

        with st.spinner(f"Modelo: {tpl.name}"):
            resp = client.chat(
                messages=[
                    {"role":"system","content": BASE_DIRECTIVES},
                    {"role":"system","content": tpl.read_text("utf-8")},
                    {"role":"user","content":  prompt_final}
                ],
                temperature=temp
            )
            api_results.append((tpl.name, clean_api(resp)))

    # Templates estáticos
    static_results = []
    for tpl in sorted(STATIC_DIR.glob("*.txt")):
        static_results.append(
            (
                substitute(tpl.name, var_map).replace("-Entity-", entity),
                substitute(tpl.read_text("utf-8"), var_map)
            )
        )

    st.session_state["api_results"]    = api_results
    st.session_state["static_results"] = static_results

    # Mostrar resultados
    st.divider(); st.subheader("✧ Templates API")
    for n,c in api_results:   st.markdown(f"**// {n}**"); st.code(c, line_numbers=True)
    st.divider(); st.subheader("✧ Templates estáticos")
    for n,c in static_results: st.markdown(f"**// {n}**"); st.code(c, line_numbers=True)

    idx = len(st.session_state["hist"])
    st.session_state["hist"].append(("assistant","✔️ Listo"))
    message("✔️ Listo", False, key=f"msg_{idx}")

# === GUARDAR ========================================
with st.sidebar:
    if st.session_state.get("api_results") or st.session_state.get("static_results"):
        if st.button("💾 Guardar TODO"):
            var_map = st.session_state["var_map"]
            saved=[]
            for n,c in st.session_state["api_results"]:
                fname = substitute(n, var_map).replace("-Entity-", entity)
                if "." not in fname: fname+=".txt"
                (out_dir/fname).write_text(c,encoding="utf-8"); saved.append(fname)
            for n,c in st.session_state["static_results"]:
                (out_dir/n).write_text(c,encoding="utf-8"); saved.append(n)
            st.success("Guardados:\n"+"\n".join(saved))
