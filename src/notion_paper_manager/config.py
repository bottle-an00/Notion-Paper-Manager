from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def _env_expand(value: str | None) -> str | None:
    if value is None:
        return None
    # ${VAR} 치환
    return os.path.expandvars(value)

def _load_yaml_config() -> dict:
    cfg_path = Path(".config/notion.yaml")
    if not cfg_path.exists():
        return {}
    with cfg_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    # ENV 치환
    def walk(v):
        if isinstance(v, str):
            return _env_expand(v)
        if isinstance(v, dict):
            return {k: walk(vv) for k, vv in v.items()}
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v
    return walk(raw)

_yaml_cfg = _load_yaml_config()

@dataclass
class DBProps:
    database_id: str
    properties: dict

def _get_section(section: str, fallback_id_env: str, default_props: dict) -> DBProps:
    block = _yaml_cfg.get(section, {})
    dbid = block.get("database_id") or os.getenv(fallback_id_env, "")
    props = block.get("properties", {}) or default_props
    return DBProps(database_id=dbid, properties=props)

_main_defaults = {
    "title": "Title",
    "year": "Year",
    "url": "URL",
    "authors": "Authors",
}

@dataclass
class Settings:
    notion_token: str = os.getenv("NOTION_TOKEN", "")
    workdir_data: str = os.getenv("WORKDIR_DATA", "data")
    workdir_output: str = os.getenv("WORKDIR_OUTPUT", "output")

    main: DBProps = field(default_factory=lambda: _get_section("main_db", "NOTION_DATABASE_ID", _main_defaults))

settings = Settings()
