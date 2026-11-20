"""
Multi-Agent Workflow Engine & Orchestrator CLI
==============================================
Ushbu modul Orchestrator boshqaruv mexanizmini to'liq avtomatlashtiradi:
- Git-Flow qoidalariga rioya qilish (develop -> feat/<name> -> merge develop -> delete feat)
- State tracking (.agents/state.json)
- Pytest natijalarini tekshirish
- Sikllar (cycles) monitoringi
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

AGENTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = AGENTS_DIR.parent.resolve()
STATE_FILE = AGENTS_DIR / "state.json"
CONFIG_FILE = AGENTS_DIR / "config.json"


def run_cmd(args: list[str], check: bool = True, cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Buyruqlarni xavfsiz ishga tushirish yordamchisi."""
    work_dir = cwd or PROJECT_ROOT
    result = subprocess.run(
        args,
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Buyruq muvaffaqiyatsiz yakunlandi: {' '.join(args)}\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class OrchestratorEngine:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()

    def _load_config(self) -> Dict[str, Any]:
        if not CONFIG_FILE.exists():
            return {
                "orchestrator": {
                    "base_branch": "develop",
                    "protected_branches": ["main", "develop"],
                    "max_review_cycles": 3,
                    "auto_merge_on_approval": True,
                    "delete_feature_branch_on_merge": True
                }
            }
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self) -> Dict[str, Any]:
        if not STATE_FILE.exists():
            default_state = {
                "phase": "IDLE",
                "task": None,
                "feature_branch": None,
                "cycle_count": 0,
                "max_cycles": self.config.get("orchestrator", {}).get("max_review_cycles", 3),
                "verdict": None,
                "history": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_state(default_state)
            return default_state
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]):
        state["last_updated"] = datetime.now().isoformat()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        self.state = state

    @property
    def base_branch(self) -> str:
        return self.config.get("orchestrator", {}).get("base_branch", "develop")

    @property
    def max_cycles(self) -> int:
        return self.config.get("orchestrator", {}).get("max_review_cycles", 3)

    def get_current_branch(self) -> str:
        _, stdout, _ = run_cmd(["git", "branch", "--show-current"])
        return stdout

    def get_status(self) -> Dict[str, Any]:
        """Tizimning joriy holatini qaytaradi."""
        current_branch = self.get_current_branch()
        _, status_out, _ = run_cmd(["git", "status", "--short"])
        return {
            "current_git_branch": current_branch,
            "git_dirty": bool(status_out),
            "uncommitted_files": status_out.splitlines() if status_out else [],
            "orchestrator_state": self.state
        }

    def start_task(self, task: str, branch_name: str) -> Dict[str, Any]:
        """
        Yangi vazifani boshlash:
        1. develop branchiga o'tadi
        2. feat/<branch_name> ochadi
        3. state ni ENGINEERING holatiga o'tkazadi
        """
        if not branch_name.startswith("feat/"):
            branch_name = f"feat/{branch_name}"

        print(f"[Orchestrator] Vazifa boshlanmoqda: '{task}'")
        print(f"[Orchestrator] Baza branch: {self.base_branch}")

        # 1. develop ga o'tish
        current = self.get_current_branch()
        if current != self.base_branch:
            run_cmd(["git", "checkout", self.base_branch])

        # 2. Branch mavjudligini tekshirish
        _, branches_out, _ = run_cmd(["git", "branch"])
        existing_branches = [b.strip().replace("* ", "") for b in branches_out.splitlines()]

        if branch_name in existing_branches:
            run_cmd(["git", "checkout", branch_name])
        else:
            run_cmd(["git", "checkout", "-b", branch_name])

        self.state["phase"] = "ENGINEERING"
        self.state["task"] = task
        self.state["feature_branch"] = branch_name
        self.state["cycle_count"] = 1
        self.state["verdict"] = "PENDING"
        self.state["history"].append({
            "event": "TASK_STARTED",
            "task": task,
            "branch": branch_name,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state(self.state)

        print(f"[Orchestrator] {branch_name} branchi ochildi va holat ENGINEERING ga o'tdi.")
        return self.state

    def run_tests(self) -> tuple[bool, str]:
        """Pytest testlarini ishga tushirish."""
        python_exe = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = "python"
        else:
            python_exe = str(python_exe)

        code, stdout, stderr = run_cmd([python_exe, "-m", "pytest", "-v"], check=False)
        output = stdout or stderr
        return (code == 0), output

    def record_review(self, verdict: str, issues: Optional[list] = None, score: int = 10) -> Dict[str, Any]:
        """Reviewer xulosasini qayd etish."""
        verdict = verdict.upper()
        if verdict not in ("APPROVED", "CHANGES_REQUESTED"):
            raise ValueError("Verdict faqat APPROVED yoki CHANGES_REQUESTED bo'lishi mumkin.")

        self.state["verdict"] = verdict
        self.state["phase"] = "REVIEWING"

        review_entry = {
            "cycle": self.state["cycle_count"],
            "verdict": verdict,
            "score": score,
            "issues": issues or [],
            "timestamp": datetime.now().isoformat()
        }
        self.state["history"].append(review_entry)

        if verdict == "CHANGES_REQUESTED":
            if self.state["cycle_count"] >= self.max_cycles:
                self.state["phase"] = "FAILED"
                print(f"[Orchestrator] XATOLIK: Maksimal review sikli ({self.max_cycles}) tugadi!")
            else:
                self.state["cycle_count"] += 1
                self.state["phase"] = "ENGINEERING"
                print(f"[Orchestrator] Tuzatish talab qilindi. Yangi sikl: {self.state['cycle_count']}/{self.max_cycles}")
        else:
            self.state["phase"] = "APPROVED"
            print("[Orchestrator] Reviewer APPROVED berdi! Merge qilishga tayyor.")

        self._save_state(self.state)
        return self.state

    def merge_and_finish(self) -> Dict[str, Any]:
        """
        APPROVED bo'lgach:
        1. develop branchiga o'tadi
        2. feature branchini --no-ff bilan merge qiladi
        3. feature branchni o'chiradi
        4. state ni COMPLETED ga o'tkazadi
        """
        feature_branch = self.state.get("feature_branch")
        if not feature_branch:
            raise RuntimeError("Faol feature branch topilmadi.")

        if self.state.get("verdict") != "APPROVED":
            raise RuntimeError("Kodni merge qilish uchun Reviewer tomonidan APPROVED berilgan bo'lishi shart!")

        print(f"[Orchestrator] {feature_branch} -> {self.base_branch} ga birlashtirilmoqda...")
        run_cmd(["git", "checkout", self.base_branch])
        run_cmd([
            "git", "merge", "--no-ff", feature_branch,
            "-m", f"Merge branch '{feature_branch}' into {self.base_branch}"
        ])

        print(f"[Orchestrator] Feature branch o'chirilmoqda: {feature_branch}")
        run_cmd(["git", "branch", "-d", feature_branch])

        self.state["phase"] = "COMPLETED"
        self.state["history"].append({
            "event": "TASK_COMPLETED",
            "branch_merged": feature_branch,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state(self.state)
        print("[Orchestrator] Vazifa muvaffaqiyatli yakunlandi!")
        return self.state

    def abort_task(self, reason: str = "Inson tomonidan bekor qilindi") -> Dict[str, Any]:
        """Vazifani bekor qilish va develop branchiga xavfsiz qaytish."""
        current = self.get_current_branch()
        if current != self.base_branch:
            run_cmd(["git", "checkout", self.base_branch], check=False)

        self.state["phase"] = "ABORTED"
        self.state["history"].append({
            "event": "TASK_ABORTED",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state(self.state)
        print(f"[Orchestrator] Vazifa bekor qilindi. Sabab: {reason}")
        return self.state


def main():
    parser = argparse.ArgumentParser(description="Evently Multi-Agent Orchestrator CLI")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Joriy workflow holatini ko'rish")

    # start
    start_parser = subparsers.add_parser("start", help="Yangi vazifani boshlash va feature branch ochish")
    start_parser.add_argument("--task", required=True, help="Vazifa nomi")
    start_parser.add_argument("--branch", required=True, help="Feature branch nomi (masalan, feat/auth)")

    # test
    subparsers.add_parser("test", help="Pytest testlarini ishga tushirish")

    # review
    review_parser = subparsers.add_parser("review", help="Review xulosasini qayd etish")
    review_parser.add_argument("--verdict", choices=["APPROVED", "CHANGES_REQUESTED"], required=True)
    review_parser.add_argument("--score", type=int, default=10)

    # finish
    subparsers.add_parser("finish", help="develop ga merge qilish va feature branchni o'chirish")

    # abort
    abort_parser = subparsers.add_parser("abort", help="Vazifani bekor qilish")
    abort_parser.add_argument("--reason", default="Bekor qilindi")

    args = parser.parse_args()
    engine = OrchestratorEngine()

    if args.command == "status":
        print(json.dumps(engine.get_status(), indent=2, ensure_ascii=False))
    elif args.command == "start":
        engine.start_task(args.task, args.branch)
    elif args.command == "test":
        success, out = engine.run_tests()
        print(out)
        sys.exit(0 if success else 1)
    elif args.command == "review":
        engine.record_review(args.verdict, score=args.score)
    elif args.command == "finish":
        engine.merge_and_finish()
    elif args.command == "abort":
        engine.abort_task(args.reason)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
