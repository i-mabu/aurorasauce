"""ASL のコマンドライン入口。

学習用言語の実行時エラーは、トレースバックではなく
日本語の短いメッセージで伝え、終了コード 1 で終わる。
"""

import argparse
import sys

from . import __version__
from .evaluator import Evaluator
from .lexer import Lexer
from .parser import Parser


def run_file(path: str) -> None:
    with open(path, encoding="utf-8") as file:
        source = file.read()

    tokens = Lexer(source).tokenize()
    statements = Parser(tokens).parse()
    Evaluator().evaluate(statements)


def _error(message: str) -> int:
    print(f"❌ {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="asl")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="ASL ファイルを実行する")
    run_parser.add_argument("file")

    args = parser.parse_args(argv)

    # ⌨️ サブコマンドは run のみのため、ここに来た時点で実行対象は決まっている。
    try:
        run_file(args.file)
    except FileNotFoundError:
        return _error(f"ファイルが見つかりません: {args.file}")
    except IsADirectoryError:
        return _error(f"ファイルを開けません（ディレクトリです）: {args.file}")
    except UnicodeDecodeError:
        return _error(f"ファイルの文字コードが UTF-8 ではありません: {args.file}")
    except OSError as error:
        return _error(f"ファイルを開けません: {args.file} ({error})")
    except SyntaxError as error:
        return _error(f"構文エラー: {error}")
    except RecursionError:
        # 🔁 RecursionError は RuntimeError のサブクラスで、そのまま出すと
        # 英語の "maximum recursion depth exceeded" になってしまう。
        return _error("入れ子が深すぎます")
    except RuntimeError as error:
        return _error(f"実行エラー: {error}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
