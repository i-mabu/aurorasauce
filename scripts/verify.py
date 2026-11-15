#!/usr/bin/env python3
"""ASL のローカル検証を一括実行するクロスプラットフォーム runner。

テスト（カバレッジ付き）・Lint・依存関係監査・Build を順に実行する。
ruff / pip-audit は `python -m` 経由で呼ぶため、venv を有効化して
いなくても、実行中の Python と同じ環境のものが使われる。
`--skip-audit` を付けると、オフライン時などに監査だけを省ける。

依存関係監査は、既知の脆弱性が見つかった場合のみ失敗させる。
ネットワークなどの環境要因で監査自体が実行できなかった場合は
警告を出して続行する（脆弱性ありと区別するため、JSON 出力を確認する）。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    print(f"\n>>> {' '.join(args)}", flush=True)
    try:
        subprocess.run(args, cwd=ROOT, check=True)
    except FileNotFoundError as error:
        raise SystemExit(
            f"❌ コマンドが見つかりません: {error.filename}\n"
            "開発依存関係を入れてください: "
            "python -m pip install -e \".[dev]\""
        ) from error


def audit_found_vulnerabilities(result: subprocess.CompletedProcess[str]) -> bool:
    """pip-audit の JSON 出力に脆弱性が含まれているかを判定する。"""
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict):
        return False
    return any(dep.get("vulns") for dep in data.get("dependencies", []))


def run_audit(python: str) -> None:
    print(f"\n>>> {python} -m pip_audit --skip-editable .", flush=True)
    result = subprocess.run(
        [python, "-m", "pip_audit", "--skip-editable", ".", "-f", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode == 0:
        print("✅ 依存関係監査が完了しました（既知の脆弱性なし）")
        return
    if audit_found_vulnerabilities(result):
        raise SystemExit(
            "❌ 依存関係に既知の脆弱性があります。"
            "詳細は上記の監査結果を確認してください。"
        )
    print(
        "⚠️ 依存関係監査を実行できませんでした"
        "（ネットワークなどの環境要因の可能性があります）。",
        file=sys.stderr,
    )
    print(
        "⚠️ 監査を省いて続行します。"
        "オフライン時は --skip-audit を使ってください。",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASL の一括検証")
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help="依存関係監査（pip-audit）を省く（オフライン時など）",
    )
    args = parser.parse_args(argv)

    python = sys.executable
    run(python, "-m", "pytest", "-q")
    run(python, "-m", "ruff", "check", ".")
    if not args.skip_audit:
        # プロジェクトの依存関係だけを監査する（実行環境の pip 自体は対象外）。
        run_audit(python)
    run(python, "-m", "build")
    artifacts = sorted((ROOT / "dist").glob("*"))
    if not artifacts:
        raise SystemExit("dist/ に Build 成果物がありません")
    print("\n✅ ASL のテスト・Lint・Build が完了しました")
    for artifact in artifacts:
        print(f"  - {artifact.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
