#!/usr/bin/env python
"""Run non-destructive regression checks for 9002 Vault LINE Bot retrieval."""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Any


DEFAULT_REPO = Path(r"C:\Users\ian35\Desktop\Claude\vault-line-bot")
DEFAULT_VAULT = Path(r"C:\Users\ian35\Documents\secondbrain")
SETUP_EXIT = 2
FAIL_EXIT = 1
PASS_EXIT = 0


@dataclass
class Case:
    name: str
    query: str
    allowed_sources: set[str]
    required_answer_substrings: list[str] = field(default_factory=list)
    forbidden_answer_substrings: list[str] = field(default_factory=list)
    required_prompt_substrings: list[str] = field(default_factory=list)
    forbidden_prompt_substrings: list[str] = field(default_factory=list)
    require_agent_call: bool | None = None
    notes: str = ""


CASES: list[Case] = [
    Case(
        name="jianzhun-close-msg",
        query="查詢建準關單MSG",
        allowed_sources={"precheck"},
        required_prompt_substrings=[
            "Python deterministic index pre-check",
            "候選文件",
            "02_Projects/0188-建準廣興廠/常用sql.md",
            "關單 Message",
            "WOClose",
        ],
        forbidden_prompt_substrings=["T5F1U21_WOClose"],
        require_agent_call=True,
    ),
    Case(
        name="yuanzhan-poclose",
        query="查詢圓展 POClose",
        allowed_sources={"precheck"},
        required_prompt_substrings=[
            "02_Projects/0182-圓展/常用SQL.md",
            "關單",
            "POClose",
        ],
        require_agent_call=True,
    ),
    Case(
        name="ambiguous-close-msg",
        query="查詢關單msg",
        allowed_sources={"candidate_list"},
        required_answer_substrings=[
            "多個可能入口",
            "02_Projects/0182-圓展/常用SQL",
            "02_Projects/0188-建準廣興廠/常用sql",
        ],
        require_agent_call=False,
    ),
    Case(
        name="jianzhun-transfer-ui-inbound",
        query="查詢建準 調撥單 UI 不能上架原因",
        allowed_sources={"precheck"},
        required_prompt_substrings=[
            "02_Projects/0188-建準廣興廠/常用sql.md",
            "調撥單 UI 不能上架原因",
            "可上架明細",
        ],
        require_agent_call=True,
    ),
    Case(
        name="songchuan-current-issues",
        query="查詢松川目前問題",
        allowed_sources={"index_hints", "fallback"},
        forbidden_prompt_substrings=[
            "02_Projects/0182-圓展/常用SQL.md",
            "02_Projects/0188-建準廣興廠/常用sql.md",
        ],
        require_agent_call=True,
        notes="Time/current-state queries should not become a high-confidence tool-file hit.",
    ),
    Case(
        name="youtrack-usage",
        query="查詢YouTrack用法",
        allowed_sources={"index_hints", "fallback"},
        forbidden_prompt_substrings=[
            "02_Projects/0182-圓展/常用SQL.md",
            "02_Projects/0188-建準廣興廠/常用sql.md",
        ],
        require_agent_call=True,
        notes="May hint Utrack/YouTrack knowledge, but must not route to unrelated SQL tool files.",
    ),
    Case(
        name="teams-automation-content",
        query="查詢teams自動化內容",
        allowed_sources={"index_hints"},
        required_prompt_substrings=[
            "Index hints",
            "必須一併 Read 原始來源檔",
            "原始需求、解法流程、關鍵判斷、限制風險與後續事項",
            "PowerAutomate",
        ],
        require_agent_call=True,
    ),
    Case(
        name="family-assets",
        query="查詢家庭資產",
        allowed_sources={"precheck"},
        required_prompt_substrings=[
            "家庭資產現況",
            "生活/20260423-家庭資產現況.md",
        ],
        forbidden_prompt_substrings=[
            "家庭合計：2,098,457",
        ],
        require_agent_call=True,
    ),
    Case(
        name="shixiang-contact-list",
        query="查詢世祥人員名單",
        allowed_sources={"index_hints", "fallback"},
        forbidden_prompt_substrings=[
            "02_Projects/0182-圓展/常用SQL.md",
            "02_Projects/0188-建準廣興廠/常用sql.md",
            "04_Knowledge/WMS通用/20260408-WMS常用SQL與API操作.md",
        ],
        require_agent_call=True,
        notes="No known stable high-confidence index entry; should avoid wrong tool-file routing.",
    ),
    Case(
        name="adps-notification-sql",
        query="查詢通知系統sql，關鍵字還有ADPS",
        allowed_sources={"precheck"},
        required_prompt_substrings=[
            "04_Knowledge/WMS通用/20260408-WMS常用SQL與API操作.md",
            "NS_M_SEND_GROUP",
            "NS_M_USER",
        ],
        forbidden_prompt_substrings=[
            "02_Projects/0182-圓展/常用SQL.md",
            "02_Projects/0188-建準廣興廠/常用sql.md",
        ],
        require_agent_call=True,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=None, help="Path to vault-line-bot repo.")
    parser.add_argument("--vault", type=Path, default=None, help="Path to secondbrain vault.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def read_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def resolve_repo(repo_arg: Path | None) -> Path:
    if repo_arg:
        return repo_arg.expanduser().resolve()
    env_repo = os.environ.get("VAULT_LINE_BOT_REPO", "").strip()
    if env_repo:
        return Path(env_repo).expanduser().resolve()
    return DEFAULT_REPO


def resolve_vault(vault_arg: Path | None, repo: Path) -> Path:
    if vault_arg:
        return vault_arg.expanduser().resolve()
    env = read_env_file(repo / ".env")
    if env.get("VAULT_DIR"):
        return Path(env["VAULT_DIR"]).expanduser().resolve()
    return DEFAULT_VAULT


def setup_import(repo: Path, vault: Path) -> Any:
    if not repo.is_dir():
        raise RuntimeError(f"Repo not found: {repo}")
    if not (repo / "main.py").is_file():
        raise RuntimeError(f"main.py not found under repo: {repo}")
    if not vault.is_dir():
        raise RuntimeError(f"Vault not found: {vault}")

    env = read_env_file(repo / ".env")
    for key, value in env.items():
        os.environ.setdefault(key, value)
    os.environ["VAULT_DIR"] = str(vault)
    os.environ.setdefault("LINE_CHANNEL_SECRET", "regression-secret")
    os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "regression-token")
    os.environ["BOT_LOG_FILE"] = str(Path(tempfile.gettempdir()) / "linebot-vault-regression.log")

    os.chdir(repo)
    sys.path.insert(0, str(repo))
    return importlib.import_module("main")


def patch_main(main_module: Any, vault: Path) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def fake_ask_agent(prompt: str, allow_write: bool = False) -> str:
        calls.append({"prompt": prompt, "allow_write": allow_write})
        return f"AGENT:{prompt[:80]}"

    main_module.ask_agent = fake_ask_agent
    main_module.VAULT_DIR = str(vault)
    main_module.KNOWLEDGE_DIR = str(vault / "04_Knowledge")
    main_module.DAILY_DIR = str(vault / "03_Daily")
    main_module.ANSWER_PAGES_DIR = str(vault / "02_Projects" / "9002-VaultLINEBot" / "LineBotResults")
    main_module.DISCUSSIONS_DIR = str(vault / "02_Projects" / "9002-VaultLINEBot" / "WebDiscussionSessions")
    main_module.log_debug = lambda message: None
    return calls


def contains_all(text: str, needles: list[str]) -> list[str]:
    return [needle for needle in needles if needle not in text]


def contains_any(text: str, needles: list[str]) -> list[str]:
    return [needle for needle in needles if needle in text]


def run_case(main_module: Any, calls: list[dict[str, Any]], case: Case) -> dict[str, Any]:
    before_count = len(calls)
    answer, source = main_module.answer_query(case.query)
    new_calls = calls[before_count:]
    prompt = new_calls[-1]["prompt"] if new_calls else ""

    failures: list[str] = []
    if source not in case.allowed_sources:
        failures.append(f"source={source!r}, expected one of {sorted(case.allowed_sources)!r}")

    if case.require_agent_call is True and not new_calls:
        failures.append("expected ask_agent call, got none")
    if case.require_agent_call is False and new_calls:
        failures.append(f"expected no ask_agent call, got {len(new_calls)}")

    missing_answer = contains_all(answer, case.required_answer_substrings)
    if missing_answer:
        failures.append(f"answer missing substrings: {missing_answer!r}")

    forbidden_answer = contains_any(answer, case.forbidden_answer_substrings)
    if forbidden_answer:
        failures.append(f"answer has forbidden substrings: {forbidden_answer!r}")

    missing_prompt = contains_all(prompt, case.required_prompt_substrings)
    if missing_prompt:
        failures.append(f"prompt missing substrings: {missing_prompt!r}")

    forbidden_prompt = contains_any(prompt, case.forbidden_prompt_substrings)
    if forbidden_prompt:
        failures.append(f"prompt has forbidden substrings: {forbidden_prompt!r}")

    return {
        "name": case.name,
        "query": case.query,
        "source": source,
        "passed": not failures,
        "failures": failures,
        "agent_calls": len(new_calls),
        "answer_preview": answer[:160],
        "prompt_preview": prompt[:240],
        "notes": case.notes,
    }


def print_text_report(payload: dict[str, Any]) -> None:
    print("LINE Bot vault regression")
    print(f"repo : {payload['repo']}")
    print(f"vault: {payload['vault']}")
    print(f"passed: {payload['passed_count']}/{payload['total']}")
    print()
    for result in payload["results"]:
        marker = "PASS" if result["passed"] else "FAIL"
        print(f"[{marker}] {result['name']} :: {result['query']} -> {result['source']}")
        for failure in result["failures"]:
            print(f"  - {failure}")
    if payload["failed_count"]:
        print()
        print("Regression failed. Block the LINE Bot search-logic change until fixed.")


def main() -> int:
    args = parse_args()
    repo = resolve_repo(args.repo)
    vault = resolve_vault(args.vault, repo)

    try:
        main_module = setup_import(repo, vault)
        calls = patch_main(main_module, vault)
        results = [run_case(main_module, calls, case) for case in CASES]
    except Exception as exc:
        payload = {
            "setup_error": str(exc),
            "repo": str(repo),
            "vault": str(vault),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"SETUP ERROR: {exc}", file=sys.stderr)
            print(f"repo : {repo}", file=sys.stderr)
            print(f"vault: {vault}", file=sys.stderr)
        return SETUP_EXIT

    failed_count = sum(1 for result in results if not result["passed"])
    payload = {
        "repo": str(repo),
        "vault": str(vault),
        "total": len(results),
        "passed_count": len(results) - failed_count,
        "failed_count": failed_count,
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return PASS_EXIT if failed_count == 0 else FAIL_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
