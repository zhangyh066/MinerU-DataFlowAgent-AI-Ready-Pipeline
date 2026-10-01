"""OpenAI 兼容接口的 LLM 客户端（urllib 实现，零额外依赖）。

默认走智谱 GLM（复用评估流水线的 DF_API_KEY），
设 RAG_LLM_PROVIDER=deepseek 或配置环境变量可切换到 DeepSeek。
"""

import json
import logging
import os
import time
import urllib.request

from .config import RAGConfig

log = logging.getLogger(__name__)

_PROVIDERS = {
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key_env": "DF_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
}


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig.from_env()
        provider = _PROVIDERS.get(self.config.llm_provider)
        if provider is None:
            raise LLMError(
                f"未知 LLM 提供商：{self.config.llm_provider}"
                f"（可选：{', '.join(_PROVIDERS)}）")
        self.base_url = os.getenv("RAG_LLM_BASE_URL", provider["base_url"])
        self.api_key_env = provider["api_key_env"]

    @property
    def api_key(self):
        return os.getenv(self.api_key_env) or os.getenv("RAG_LLM_API_KEY")

    def chat(self, prompt, system=None, temperature=0.3):
        """发送一次对话请求，带重试与指数退避。"""
        key = self.api_key
        if not key:
            raise LLMError(
                f"未设置 {self.api_key_env}（或通用的 RAG_LLM_API_KEY）")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        last_err = None
        for attempt in range(self.config.llm_retries + 1):
            try:
                req = urllib.request.Request(
                    self.base_url,
                    data=json.dumps({
                        "model": self.config.llm_model,
                        "messages": messages,
                        "temperature": temperature,
                        "stream": False,
                    }).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + key,
                    },
                )
                with urllib.request.urlopen(req, timeout=self.config.llm_timeout) as r:
                    data = json.loads(r.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
            except Exception as e:  # 网络错误、限流、5xx 都按可重试处理
                last_err = e
                if attempt < self.config.llm_retries:
                    wait = 2 ** attempt * 2
                    log.warning("LLM 请求失败（%s），%d 秒后重试", e, wait)
                    time.sleep(wait)
        raise LLMError(f"LLM 请求多次失败：{last_err}")
