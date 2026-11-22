# 🍅 Aurora Sauce Language

オーロラソースをテーマにした、学習用の小さなプログラミング言語処理系。

> Code it. Mix it. Taste it.

## 🚧 状態

初期開発段階です。言語仕様と実装は確定していません。

## 🧪 現在の実装範囲

- `say "...";` の字句解析・構文解析・評価
- コメント、文字列、行番号付き構文エラー
- `asl run examples/hello.asl` による実行
- 変数と計算（Phase 2a）：`add 名前 = 式;` による宣言、代入による書き換え、数値・四則演算・括弧・文字列結合
- `asl run examples/ingredients.asl` による実行例
- 条件分岐（Phase 2b）：`if` / `else`、`== != < <= > >=` による比較、真偽値 `true` / `false`（条件は真偽値必須）
- `asl run examples/tasting.asl` による実行例
- 繰り返し（Phase 2c）：`repeat N { ... }`（回数は数値リテラル・変数・式、0 なら 0 回、負数・小数・文字列はエラー）
- `asl run examples/stirring.asl` による実行例
- CLI のエラー境界：ファイルなし・構文エラー・実行エラーを日本語の短いメッセージで表示し、終了コード 1 で終わる（トレースバックは出さない）
- `asl --version` によるバージョン表示
- カバレッジ計測（下限 90%）と CLI の E2E テスト、依存関係監査

言語仕様と実装は初期段階です。仕様を変更する場合は、テストと `ARCHITECTURE.md` を同時に更新してください。

## 🚀 セットアップ

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 🧪 検証

一括検証（テスト・カバレッジ・Lint・依存関係監査・Build）:

```sh
python scripts/verify.py
# オフライン時など、監査だけ省く場合
python scripts/verify.py --skip-audit
```

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
python -m pip_audit --skip-editable .
python -m build
```

テストはカバレッジ下限 90% で実行されます。監査はプロジェクトの
依存関係だけが対象で、実行環境の pip 自体は対象外です。

## ▶️ サンプル実行

```bash
asl run examples/hello.asl
asl run examples/ingredients.asl
asl run examples/tasting.asl
asl run examples/stirring.asl
```

## 📚 文書

- [開発ガイド](DEVELOPMENT.md)
- [テスト方針](TESTING.md)
- [アーキテクチャ](ARCHITECTURE.md)
- [セキュリティ](SECURITY.md)
- [ロードマップ](ROADMAP.md)
- [変更履歴](CHANGELOG.md)

## 📄 ライセンス

Aurora Sauce Language は、
[Apache License, Version 2.0](LICENSE) のもとでライセンスされています。
