"""
Multi-Agent Workflow Engine
===========================
Ushbu skript 4 ta agent (Orchestrator, Architect, Engineer, Reviewer) o'rtasidagi
aloqa va Git-Flow oqimini avtomatlashtiradi.

Workflow:
1. User Prompt qabul qilinadi.
2. Architect loyihalaydi va feat branch nomini belgilaydi.
3. develop dan feat/<task-name> branchi ochiladi.
4. Engineer kod va testlarni faqat shu branchda yozadi.
5. Reviewer tekshiradi:
   - CHANGES_REQUESTED -> Engineer ga qaytadi (maksimal 3 sikl).
   - APPROVED -> develop ga merge qilinadi va feat branch o'chiriladi.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

AGENTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = AGENTS_DIR.parent.resolve()


def run_git(args: list[str], check: bool = True) -> str:
    """Git buyruqlarini xavfsiz ishga tushirish yordamchisi."""
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Git xatolik: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


class AgentWorkflow:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = AGENTS_DIR / "config.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.base_branch = self.config.get("orchestrator", {}).get("base_branch", "develop")
        self.max_cycles = self.config.get("orchestrator", {}).get("max_review_cycles", 3)
        self.protected_branches = self.config.get("orchestrator", {}).get("protected_branches", ["main", "develop"])
        self.state: Dict[str, Any] = {
            "phase": "IDLE",
            "task": None,
            "feature_branch": None,
            "cycle_count": 0,
            "verdict": None
        }

    def load_prompt(self, agent_name: str) -> str:
        """Har bir agentning tizim promptini o'qish."""
        agent_cfg = self.config.get("agents", {}).get(agent_name)
        if not agent_cfg:
            raise ValueError(f"Noma'lum agent: {agent_name}")
        
        agent_path = AGENTS_DIR / agent_cfg["path"]
        if not agent_path.exists():
            raise FileNotFoundError(f"Agent fayli topilmadi: {agent_path}")
            
        return agent_path.read_text(encoding="utf-8")

    def ensure_base_branch(self):
        """Asosiy develop branchiga o'tish va tozaligini tekshirish."""
        print(f"[Orchestrator] Baza branch: {self.base_branch} tekshirilmoqda...")
        current_branch = run_git(["branch", "--show-current"])
        
        # Agar hozirgi branch develop bo'lmasa, develop ga o'tamiz
        if current_branch != self.base_branch:
            print(f"[Orchestrator] {self.base_branch} branchiga o'tilmoqda...")
            run_git(["checkout", self.base_branch])

    def create_feature_branch(self, branch_name: str):
        """develop branchidan yangi feature branch ochish."""
        self.ensure_base_branch()
        print(f"[Git-Flow] Yangi feature branch ochilmoqda: {branch_name}")
        
        # Agar branch allaqachon mavjud bo'lsa, unga o'tish, aks holda yangi yaratish
        branches = run_git(["branch"]).split()
        if branch_name in branches:
            run_git(["checkout", branch_name])
        else:
            run_git(["checkout", "-b", branch_name])
            
        self.state["feature_branch"] = branch_name
        self.state["phase"] = "ENGINEERING"

    def merge_and_cleanup(self, branch_name: str):
        """Reviewer APPROVED bergach develop ga merge qilish va feature branchni o'chirish."""
        print(f"[Git-Flow] Reviewer APPROVED berdi! {branch_name} -> {self.base_branch} ga merge qilinmoqda...")
        run_git(["checkout", self.base_branch])
        run_git(["merge", "--no-ff", branch_name, "-m", f"merge: {branch_name} into {self.base_branch}"])
        print(f"[Git-Flow] Ishlatilgan branch o'chirilmoqda: {branch_name}")
        run_git(["branch", "-d", branch_name])
        self.state["phase"] = "COMPLETED"
        print("[Orchestrator] Vazifa muvaffaqiyatli yakunlandi va develop branchiga qo'shildi!")

    def run_lifecycle(self, user_prompt: str, mock_review_passes_at_cycle: int = 2):
        """
        To'liq simulyatsiya va ish jarayoni:
        1. Architect bosqichi
        2. Feature branch yaratish
        3. Engineer <-> Reviewer tsikli (max 3 marta)
        4. Muvaffaqiyatli yakun
        """
        print(f"\n==========================================")
        print(f"[Orchestrator] Yangi vazifa qabul qilindi: {user_prompt}")
        print(f"==========================================\n")
        
        self.state["task"] = user_prompt
        self.state["phase"] = "ARCHITECTING"
        
        # 1. Architect chaqiruvi
        print("[Phase 1: Architect] Loyiha arxitekturasi va stacki tahlil qilinmoqda...")
        architect_prompt = self.load_prompt("architect")
        # Misol uchun branch nomi
        suggested_branch = "feat/initial-setup-test"
        print(f"[Architect] Tavsiya etilgan branch: {suggested_branch}")
        
        # 2. Git Branch yaratish
        self.create_feature_branch(suggested_branch)
        
        # 3. Engineer va Reviewer sikli
        cycle = 0
        while cycle < self.max_cycles:
            cycle += 1
            self.state["cycle_count"] = cycle
            print(f"\n--- SIKL {cycle} / {self.max_cycles} ---")
            
            # Engineer kodi
            print(f"[Phase 2: Engineer] Kod va testlar faqat {suggested_branch} branchida yozilmoqda...")
            
            # Reviewer tekshiruvi
            print(f"[Phase 3: Reviewer] Kod va diff tekshirilmoqda...")
            if cycle < mock_review_passes_at_cycle:
                print(f"[Reviewer] Verdict: CHANGES_REQUESTED (Kamchiliklar aniqlandi, Engineer ga qaytariladi)")
                self.state["verdict"] = "CHANGES_REQUESTED"
                continue
            else:
                print(f"[Reviewer] Verdict: APPROVED (Barcha testlar o'tdi, sifat talablariga mos)")
                self.state["verdict"] = "APPROVED"
                break
                
        # 4. Natijani tekshirish
        if self.state["verdict"] == "APPROVED":
            self.merge_and_cleanup(suggested_branch)
            return True
        else:
            print(f"[Orchestrator] DIQQAT: {self.max_cycles} ta siklda kod tasdiqlanmadi. Inson aralashuvi talab qilinadi.")
            self.state["phase"] = "FAILED"
            return False


if __name__ == "__main__":
    workflow = AgentWorkflow()
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Evently loyihasida health check endpointini yaratish"
    success = workflow.run_lifecycle(prompt, mock_review_passes_at_cycle=2)
    sys.exit(0 if success else 1)
