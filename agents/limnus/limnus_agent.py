from __future__ import annotations

"""Limnus Agent (Memory Engine & Ledger Steward)

Commands:
- cache <text>
- recall [query]
- commit_block(kind, data)
- encode_ledger / decode_ledger (stubs)

Maintains:
- state/limnus_memory.json (list of {ts, text, tags})
- state/ledger.json (hash-chained blocks)
"""
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from interface.logger import log_event


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class Block:
    ts: str
    kind: str
    data: Dict[str, Any]
    prev: str
    hash: str


class LimnusAgent:
    def __init__(self, root: Path):
        self.root = root
        self.mem_path = self.root / "state" / "limnus_memory.json"
        self.ledger_path = self.root / "state" / "ledger.json"
        for p in [self.mem_path, self.ledger_path]:
            p.parent.mkdir(parents=True, exist_ok=True)
        if not self.mem_path.exists():
            self.mem_path.write_text("[]", encoding="utf-8")
        if not self.ledger_path.exists():
            self._init_ledger()

    def _init_ledger(self) -> None:
        genesis = {"ts": _ts(), "kind": "genesis", "data": {"anchor": "I return as breath."}, "prev": ""}
        content = json.dumps(genesis, sort_keys=True)
        genesis["hash"] = _sha256(content)
        self.ledger_path.write_text(json.dumps([genesis], indent=2), encoding="utf-8")

    def _read_ledger(self) -> List[Dict[str, Any]]:
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def _write_ledger(self, blocks: List[Dict[str, Any]]) -> None:
        self.ledger_path.write_text(json.dumps(blocks, indent=2), encoding="utf-8")

    def cache(self, text: str) -> str:
        mem = json.loads(self.mem_path.read_text(encoding="utf-8"))
        mem.append({"ts": _ts(), "text": text, "tags": []})
        self.mem_path.write_text(json.dumps(mem, indent=2), encoding="utf-8")
        log_event("limnus", "cache", {"text": text})
        return "cached"

    def recall(self, query: Optional[str] = None) -> str:
        mem = json.loads(self.mem_path.read_text(encoding="utf-8"))
        if not query:
            return json.dumps(mem)
        q = query.lower()
        hits = [m for m in mem if q in m.get("text", "").lower()]
        return json.dumps(hits)

    def commit_block(self, kind: str, data: Dict[str, Any]) -> str:
        blocks = self._read_ledger()
        prev_hash = blocks[-1]["hash"] if blocks else ""
        block = {"ts": _ts(), "kind": kind, "data": data, "prev": prev_hash}
        block["hash"] = _sha256(json.dumps(block, sort_keys=True))
        blocks.append(block)
        self._write_ledger(blocks)
        log_event("limnus", "commit_block", {"kind": kind})
        return block["hash"]

    # Stubs for stego
    def encode_ledger(self, out_path: str | None = None) -> str:
        """Embed the ledger payload into a simple artifact.

        If Pillow is available, write a small PNG placeholder with the JSON
        stored in a sibling `.json` file. Otherwise, write the JSON to
        `frontend/assets/ledger.json`.
        Returns the path to the produced artifact.
        """
        assets = self.root / "frontend" / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        ledger_json = json.dumps(self._read_ledger(), ensure_ascii=False)
        # Always write JSON alongside
        json_path = assets / "ledger.json"
        json_path.write_text(ledger_json, encoding="utf-8")
        artifact = json_path
        try:
            from PIL import Image  # type: ignore

            img = Image.new("RGBA", (64, 64), (10, 14, 20, 255))
            png_path = assets / "ledger.png"
            img.save(png_path)
            artifact = png_path
        except Exception:
            # Pillow not available; JSON artifact only
            pass
        log_event("limnus", "encode_ledger", {"out": str(artifact)})
        return str(artifact)

    def decode_ledger(self, src: str | None = None) -> str:
        # Minimal: return current ledger JSON
        payload = json.dumps(self._read_ledger())
        log_event("limnus", "decode_ledger", {"src": src})
        return payload
