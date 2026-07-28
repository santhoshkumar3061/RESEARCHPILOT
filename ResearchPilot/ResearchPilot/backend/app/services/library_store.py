"""
Library persistence layer.

Uses a JSON file on disk to keep the demo dependency-free. In production
this would be swapped for Postgres (SQLAlchemy models mirroring
LibraryItem) without changing the router-facing function signatures below.
"""
import json
import threading
from pathlib import Path

from app.models.schemas import LibraryItem

_LOCK = threading.Lock()
_STORE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "library.json"
_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_all() -> dict[str, dict]:
    if not _STORE_PATH.exists():
        return {}
    with open(_STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_all(data: dict[str, dict]) -> None:
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str, indent=2)


def list_items() -> list[LibraryItem]:
    with _LOCK:
        return [LibraryItem(**v) for v in _read_all().values()]


def get_item(paper_id: str) -> LibraryItem | None:
    with _LOCK:
        raw = _read_all().get(paper_id)
        return LibraryItem(**raw) if raw else None


def upsert_item(item: LibraryItem) -> LibraryItem:
    with _LOCK:
        data = _read_all()
        data[item.paper.id] = json.loads(item.model_dump_json())
        _write_all(data)
        return item


def delete_item(paper_id: str) -> bool:
    with _LOCK:
        data = _read_all()
        if paper_id in data:
            del data[paper_id]
            _write_all(data)
            return True
        return False
