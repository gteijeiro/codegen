# model_client.py
"""
Adaptador de modelo.  Hoy trae la implementación para Azure OpenAI;
mañana puedes agregar otro provider (OpenAI, Ollama, Anthropic, etc.)
manteniendo la misma interfaz.

Uso:
    from model_client import ModelClient
    client = ModelClient.from_secrets()        # lee .streamlit/secrets.toml
    text = client.chat(messages, temperature=0.7)
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import streamlit as st

# ───────── Interfaz ─────────────────────────────────────────
@dataclass
class ModelClient:
    provider: str
    config: Dict[str, Any]

    # instancia “real” del SDK (Azure, OpenAI, etc.)
    _client: Any = None
    _model:  str = ""

    # -------- CONSTRUCTORES ---------------------------------
    @classmethod
    def from_secrets(cls) -> "ModelClient":
        cfg = st.secrets["model_deepseek"]              # requiere bloque [model]
        return cls(provider=cfg.get("provider", "azure_deepseek"),
                   config=cfg)

    def __post_init__(self):
        if self.provider == "azure_deepseek":
            # Carga perezosa sólo si se usa este provider
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential

            self._client = ChatCompletionsClient(
                endpoint   = self.config["endpoint"],
                credential = AzureKeyCredential(self.config["api_key"]),
            )
            self._model = self.config["model_name"]

        else:
            raise ValueError(f"Proveedor {self.provider!r} no soportado aún")

    # -------- API ÚNICA -------------------------------------
    def chat(self,
             messages: List[Dict[str, str]],
             temperature: float = 0.7,
             max_tokens: int = 4096) -> str:

        resp = self._client.complete(
            messages     = messages,
            model        = self._model,
            temperature  = temperature,
            max_tokens   = max_tokens,
        )
        return resp.choices[0].message.content

        # Si hubiera otros providers, despachamos aquí…
        raise RuntimeError("Provider no implementado")
