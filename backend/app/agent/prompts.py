import os
import re
from pathlib import Path

_HERE = Path(__file__).parent


def _load(filename: str) -> str:
    path = _HERE / filename
    return path.read_text(encoding="utf-8")


def get_system_prompt() -> str:
    return _load("system_prompt.txt")


def get_user_message(**kwargs) -> str:
    template = _load("user_template.txt")
    return _inject(template, kwargs)


def get_embedding_doc() -> str:
    return _load("embedding_doc.txt")


def _inject(template: str, variables: dict) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1)
        return str(variables.get(key, match.group(0)))
    return re.sub(r"\{\{(\w+)\}\}", replace, template)
