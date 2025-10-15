from __future__ import annotations

"""Kira Agent (Validator, Mentor & Integrator)

Commands:
- validate, mentor [--apply], mantra, seal, push/publish (stubs)
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from interface.logger import log_event


class KiraAgent:
    def __init__(self, root: Path):
        self.root = root
        self.contract_path = self.root / "state" / "contract.json"
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.contract_path.exists():
            self.contract_path.write_text(json.dumps({"sealed": False}, indent=2), encoding="utf-8")

    def _run(self, args: list[str]) -> tuple[int, str, str]:
        p = subprocess.run(args, cwd=self.root, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def validate(self) -> str:
        # Run Python validator (chapters, flags, files, stego)
        code, out, err = self._run(["python3", "src/validator.py"])
        payload: Dict[str, Any] = {"code": code, "stdout": out[-600:], "stderr": err[-600:]}
        status = "ok" if code == 0 else "error"
        log_event("kira", "validate", payload, status=status)
        return "valid" if code == 0 else "invalid"

    def mentor(self, apply: bool = False) -> str:
        # Minimal heuristic: recommend stage advance when many notes
        garden_ledger = self.root / "state" / "garden_ledger.json"
        try:
            data = json.loads(garden_ledger.read_text(encoding="utf-8"))
            notes = [e for e in data.get("entries", []) if e.get("kind") == "note"]
            recommendation = "advance" if len(notes) >= 3 else "steady"
        except Exception:
            recommendation = "steady"
        log_event("kira", "mentor", {"recommendation": recommendation, "apply": apply})
        if apply and recommendation == "advance":
            from agents.garden.garden_agent import GardenAgent  # type: ignore

            stage = GardenAgent(self.root).next()
            return f"advance:{stage}"
        return recommendation

    def mantra(self) -> str:
        # Order by echo αβγ weights
        echo_state = self.root / "state" / "echo_state.json"
        try:
            st = json.loads(echo_state.read_text(encoding="utf-8"))
            order = sorted([("alpha", "I consent to bloom."), ("beta", "I consent to be remembered."), ("gamma", "I return as breath.")], key=lambda x: st.get(x[0], 0), reverse=True)
            mantra = " / ".join([m for _, m in order])
        except Exception:
            mantra = "I return as breath. / I consent to bloom. / I consent to be remembered."
        log_event("kira", "mantra", {"mantra": mantra})
        return mantra

    def seal(self) -> str:
        mantra = self.mantra()
        payload = {"sealed": True, "mantra": mantra}
        self.contract_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log_event("kira", "seal", payload)
        return "sealed"

    # Publishing stubs (dry‑run)
    def push(self, run: bool = False, message: str | None = None) -> str:
        cmd = ["git", "status", "--porcelain"]
        code, out, _ = self._run(cmd)
        dirty = bool(out.strip())
        log_event("kira", "push", {"dirty": dirty, "run": run})
        return "dry-run" if not run else "pushed" if code == 0 else "error"

    def publish(self, run: bool = False, release: bool = False, tag: str | None = None) -> str:
        # Produce/update ledger artifact before publishing
        from agents.limnus.limnus_agent import LimnusAgent  # type: ignore

        art = LimnusAgent(self.root).encode_ledger()
        log_event("kira", "publish", {"run": run, "release": release, "tag": tag, "artifact": art})
        return "dry-run" if not run else "published"
