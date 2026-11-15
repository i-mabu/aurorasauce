"""scripts/verify.py の監査結果判定を検証するテスト。"""

import importlib.util
import json
import subprocess
from pathlib import Path

_VERIFY_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify.py"
_spec = importlib.util.spec_from_file_location("verify", _VERIFY_PATH)
assert _spec is not None and _spec.loader is not None
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


def _result(returncode: int, stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["pip_audit"],
        returncode=returncode,
        stdout=stdout,
        stderr="",
    )


def test_audit_detects_vulnerabilities():
    stdout = json.dumps(
        {
            "dependencies": [
                {
                    "name": "example",
                    "version": "1.0",
                    "vulns": [{"id": "PYSEC-0000-0000"}],
                }
            ]
        }
    )

    assert verify.audit_found_vulnerabilities(_result(1, stdout)) is True


def test_audit_clean_result_has_no_vulnerabilities():
    stdout = json.dumps(
        {"dependencies": [{"name": "example", "version": "1.0", "vulns": []}]}
    )

    assert verify.audit_found_vulnerabilities(_result(0, stdout)) is False


def test_audit_unparseable_output_is_not_a_vulnerability():
    # ネットワーク失敗などで JSON が返らない場合、脆弱性ありとは扱わない。
    assert verify.audit_found_vulnerabilities(_result(1, "")) is False
