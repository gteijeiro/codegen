# model_client_azure_preview.py
"""
Adaptador para el endpoint “2024-12-01-preview” de Azure OpenAI
(o3-mini, etc.).  Uso:

    from model_client_azure_preview import ModelClient
    client = ModelClient.from_secrets()
    text   = client.chat(messages, temperature=0.7)
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import streamlit as st

@dataclass
class ModelClient:
    endpoint: str
    api_key: str
    deployment: str
    api_version: str

    _client: Any = None        # instancia de AzureOpenAI

    # -------------------- Factory --------------------
    @classmethod
    def from_secrets(cls) -> "ModelClient":
        cfg = st.secrets["model_preview"]          # nueva sección
        return cls(
            endpoint   = cfg["endpoint"],
            api_key    = cfg["api_key"],
            deployment = cfg["deployment"],
            api_version= cfg.get("api_version", "2024-12-01-preview"),
        )

    # -------------------- Inicialización -------------
    def __post_init__(self):
        from openai import AzureOpenAI
        self._client = AzureOpenAI(
            api_version    = self.api_version,
            azure_endpoint = self.endpoint,
            api_key        = self.api_key,
        )

    # -------------------- API única ------------------
    def chat(self,
             messages: List[Dict[str, str]],
             temperature: float = 0.5,
             max_tokens: int = 4096) -> str:

        resp = self._client.chat.completions.create(
            messages             = messages,
            model                = self.deployment,
            max_completion_tokens= max_tokens,
            #temperature          = temperature,
        )
        return resp.choices[0].message.content
