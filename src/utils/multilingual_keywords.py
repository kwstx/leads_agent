# Multilingual keywords for lead generation related to AI agents and development issues

KEYWORDS = {
    "en": [
        "AI agents",
        "Agentic AI",
        "multi-agent systems",
        "LangChain error",
        "AutoGPT bugs",
        "LLM integration issue",
        "agent communication failure",
        "AI automation problems"
    ],
    "zh": [
        "智能体 AI",
        "多智能体系统",
        "AI 自动化",
        "Agent 开发",
        "大语言模型插件",
        "LangChain 错误",
        "AI 代理",
        "大模型集成问题"
    ],
    "es": [
        "Agentes de IA",
        "IA agéntica",
        "Sistemas multi-agente",
        "Errores de LangChain",
        "Automatización con IA",
        "Problemas de integración de LLM",
        "Fallo de comunicación entre agentes"
    ],
    "pt": [
        "Agentes de IA",
        "IA agêntica",
        "Sistemas multiagente",
        "Erros de LangChain",
        "Automação via IA",
        "Problemas de integração LLM",
        "Falha na comunicação de agentes"
    ],
    "ja": [
        "エージェント AI",
        "マルチエージェント",
        "AI 自動化",
        "LangChain エラー",
        "AutoGPT 不具合",
        "LLM 連携の問題",
        "エージェント間通信の失敗"
    ]
}

def get_all_keywords():
    """Returns a flattened list of all keywords across all languages."""
    all_kw = []
    for lang_kw in KEYWORDS.values():
        all_kw.extend(lang_kw)
    return list(set(all_kw))

def get_keywords_by_lang(lang_code):
    """Returns keywords for a specific language code."""
    return KEYWORDS.get(lang_code, KEYWORDS["en"])

def get_combined_query(lang_code=None):
    """Returns an OR-separated query string for search APIs."""
    if lang_code:
        kws = get_keywords_by_lang(lang_code)
    else:
        kws = get_all_keywords()
    
    # Wrap multi-word keywords in quotes for better search accuracy
    quoted_kws = [f'"{kw}"' if " " in kw else kw for kw in kws]
    return " OR ".join(quoted_kws)
