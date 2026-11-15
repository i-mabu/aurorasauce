"""CLI の E2E テスト。

`python -m asl.cli` を子プロセスで実行し、実際の `asl run` と
同じ経路（引数解析・終了コード・標準出力／標準エラー）を確認する。
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "asl.cli", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_e2e_runs_hello_example():
    result = run_cli("run", "examples/hello.asl")

    assert result.returncode == 0
    assert result.stdout == "AURORA: Hello, Aurora!\n"
    assert result.stderr == ""


def test_e2e_missing_file_has_no_traceback():
    result = run_cli("run", "no-such-file.asl")

    assert result.returncode == 1
    assert "ファイルが見つかりません" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_runs_ingredients_example():
    result = run_cli("run", "examples/ingredients.asl")

    assert result.returncode == 0
    assert result.stdout == (
        "AURORA: 100\n"
        "AURORA: 150\n"
        "AURORA: 350\n"
        "AURORA: 合計: 350g\n"
        "AURORA: 2.5\n"
    )
    assert result.stderr == ""


def test_e2e_runs_tasting_example():
    result = run_cli("run", "examples/tasting.asl")

    assert result.returncode == 0
    assert result.stdout == (
        "AURORA: 甘い！\n" "AURORA: ぴったり\n" "AURORA: true\n" "AURORA: true\n"
    )
    assert result.stderr == ""


def test_e2e_runs_stirring_example():
    result = run_cli("run", "examples/stirring.asl")

    assert result.returncode == 0
    assert result.stdout == (
        "AURORA: かき混ぜる\n"
        "AURORA: かき混ぜる\n"
        "AURORA: かき混ぜる\n"
        "AURORA: もう一度\n"
        "AURORA: もう一度\n"
    )
    assert result.stderr == ""


def test_e2e_negative_repeat_has_no_traceback(tmp_path):
    source = tmp_path / "bad.asl"
    source.write_text('repeat -1 { say "a"; }\n', encoding="utf-8")

    result = run_cli("run", str(source))

    assert result.returncode == 1
    assert "実行エラー" in result.stderr
    assert "repeat の回数は 0 以上で書いてください" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_non_bool_condition_has_no_traceback(tmp_path):
    source = tmp_path / "bad.asl"
    source.write_text('add x = 1;\nif x { say "a"; }\n', encoding="utf-8")

    result = run_cli("run", str(source))

    assert result.returncode == 1
    assert "実行エラー" in result.stderr
    assert "if の条件は true か false で書いてください" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_syntax_error_has_no_traceback(tmp_path):
    source = tmp_path / "bad.asl"
    source.write_text('say "Hello"\n', encoding="utf-8")

    result = run_cli("run", str(source))

    assert result.returncode == 1
    assert "構文エラー" in result.stderr
    assert "';' が必要です" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_undefined_variable_has_no_traceback(tmp_path):
    source = tmp_path / "bad.asl"
    source.write_text("say sugar;\n", encoding="utf-8")

    result = run_cli("run", str(source))

    assert result.returncode == 1
    assert "実行エラー" in result.stderr
    assert "変数 'sugar' は定義されていません" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_unknown_keyword_has_no_traceback(tmp_path):
    source = tmp_path / "bad.asl"
    source.write_text('foo "Hello";\n', encoding="utf-8")

    result = run_cli("run", str(source))

    assert result.returncode == 1
    assert "構文エラー" in result.stderr
    assert "Traceback" not in result.stderr


def test_e2e_version():
    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stdout.startswith("asl ")


def test_e2e_no_command_exits_with_usage():
    result = run_cli()

    assert result.returncode == 2
    assert "usage:" in result.stderr
