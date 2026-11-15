"""CLI のエラー境界をプロセス内で検証するテスト。

終了コードと日本語メッセージを確認する。実際の `asl` コマンドを
子プロセスで動かす E2E は tests/test_cli_e2e.py を参照。
"""

from pathlib import Path

import pytest

from asl.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_main_runs_hello_example(capsys):
    assert main(["run", str(ROOT / "examples" / "hello.asl")]) == 0

    captured = capsys.readouterr()
    assert captured.out == "AURORA: Hello, Aurora!\n"
    assert captured.err == ""


def test_main_reports_missing_file(capsys):
    assert main(["run", "no-such-file.asl"]) == 1

    captured = capsys.readouterr()
    assert "ファイルが見つかりません" in captured.err
    assert "no-such-file.asl" in captured.err
    assert "Traceback" not in captured.err


def test_main_runs_ingredients_example(capsys):
    assert main(["run", str(ROOT / "examples" / "ingredients.asl")]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        "AURORA: 100\n"
        "AURORA: 150\n"
        "AURORA: 350\n"
        "AURORA: 合計: 350g\n"
        "AURORA: 2.5\n"
    )
    assert captured.err == ""


def test_main_runs_tasting_example(capsys):
    assert main(["run", str(ROOT / "examples" / "tasting.asl")]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        "AURORA: 甘い！\n" "AURORA: ぴったり\n" "AURORA: true\n" "AURORA: true\n"
    )
    assert captured.err == ""


def test_main_runs_stirring_example(capsys):
    assert main(["run", str(ROOT / "examples" / "stirring.asl")]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        "AURORA: かき混ぜる\n"
        "AURORA: かき混ぜる\n"
        "AURORA: かき混ぜる\n"
        "AURORA: もう一度\n"
        "AURORA: もう一度\n"
    )
    assert captured.err == ""


def test_main_reports_negative_repeat(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_text('repeat -1 { say "a"; }\n', encoding="utf-8")

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "実行エラー" in captured.err
    assert "repeat の回数は 0 以上で書いてください" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_non_bool_condition(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_text('add x = 1;\nif x { say "a"; }\n', encoding="utf-8")

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "実行エラー" in captured.err
    assert "if の条件は true か false で書いてください" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_syntax_error(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_text('say "Hello"\n', encoding="utf-8")

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "構文エラー" in captured.err
    assert "';' が必要です" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_unknown_keyword(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_text('foo "Hello";\n', encoding="utf-8")

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "構文エラー" in captured.err
    assert "'=' が必要です" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_undefined_variable(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_text('say sugar;\n', encoding="utf-8")

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "実行エラー" in captured.err
    assert "変数 'sugar' は定義されていません" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_directory(tmp_path, capsys):
    assert main(["run", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "ファイルを開けません" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_non_utf8_file(tmp_path, capsys):
    source = tmp_path / "bad.asl"
    source.write_bytes(b'say "\xff";\n')

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "UTF-8 ではありません" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_os_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / "ok.asl"
    source.write_text('say "Hello";\n', encoding="utf-8")

    def _boom(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr("builtins.open", _boom)

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "ファイルを開けません" in captured.err
    assert "Traceback" not in captured.err


def test_main_reports_runtime_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / "ok.asl"
    source.write_text('say "Hello";\n', encoding="utf-8")

    class _BoomEvaluator:
        def evaluate(self, statements):
            raise RuntimeError("boom")

    monkeypatch.setattr("asl.cli.Evaluator", _BoomEvaluator)

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "実行エラー: boom" in captured.err
    assert "Traceback" not in captured.err


def test_main_version(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--version"])

    assert error.value.code == 0
    assert capsys.readouterr().out.startswith("asl ")


def test_main_requires_command():
    with pytest.raises(SystemExit) as error:
        main([])

    assert error.value.code == 2


def test_main_reports_deep_nesting_in_japanese(tmp_path, capsys):
    source = tmp_path / "deep.asl"
    source.write_text(
        "say " + "(" * 2000 + "1" + ")" * 2000 + ";", encoding="utf-8"
    )

    assert main(["run", str(source)]) == 1

    captured = capsys.readouterr()
    assert "入れ子が深すぎます" in captured.err
    assert "Traceback" not in captured.err
    assert "maximum recursion" not in captured.err
