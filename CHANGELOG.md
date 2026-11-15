# 📜 変更履歴

## [Unreleased]

### 追加

- 🛠️ 開発、貢献、テスト、セキュリティ、アーキテクチャ、リリース、ロードマップ文書
- 🧪 CI とローカル検証方針
- 🇯🇵 日本語・絵文字を基本とするユーザー向け表示方針
- 📊 カバレッジ計測（pytest-cov、下限 90%）
- 🧪 CLI の E2E テスト（正常系・ファイルなし・構文エラー・バージョン表示）
- 🔍 依存関係監査（pip-audit）を `scripts/verify.py` に組み込み
- ℹ️ `asl --version` によるバージョン表示
- 🥕 変数と計算（Phase 2a）：`add` による変数宣言、代入による書き換え、数値・四則演算・括弧・文字列結合
- 🧪 サンプル `examples/ingredients.asl` を追加
- 🍳 条件分岐（Phase 2b）：`if` / `else`、比較演算子 `== != < <= > >=`、真偽値 `true` / `false`（条件は真偽値必須）
- 🧪 サンプル `examples/tasting.asl` を追加
- 🔁 繰り返し（Phase 2c）：`repeat N { ... }`（回数は数値リテラル・変数・式、0 なら 0 回、負数・小数・文字列はエラー）
- 🧪 サンプル `examples/stirring.asl` を追加

### 変更

- 🖥️ CLI のエラー表示：トレースバックではなく日本語の短いメッセージと終了コード 1 で返す
- 🧪 `scripts/verify.py`：ruff / pip-audit を `python -m` 経由で呼ぶようにし、venv 未アクティブでも動作する
- 🖥️ `say` が文字列だけでなく数値・変数・計算結果も受け取るように
- 🖥️ 構文エラーのメッセージを日本語化（`';' が必要です` など）
- 🔤 Lexer が未知の単語をエラーにしていたのを、識別子（変数名）として扱うように
- 🖥️ 真偽値は `true` / `false` と表示する（Python の `True` / `False` ではない）

### 修正

- 🐛 数値と真偽値の等値比較：`1 == true` が真になっていた（Python の bool が int のサブクラスのため）。真偽値とそれ以外は等しくないものとして扱う
- 🐛 `repeat` の回数が無限大・NaN のとき `int()` 変換でトレースバックになっていた問題を修正（`float.is_integer()` で判定）
- 🐛 巨大な整数と小数の混合演算・割り算で `OverflowError` のトレースバックになっていた問題を修正（実行エラーとして表示）
- 🐛 上付き数字（`²` など `int()` で変換できない文字）を数値リテラルとして拾い、Parser でトレースバックになっていた問題を修正（数字は ASCII のみ）
- 🐛 桁数の大きすぎる数値リテラルがトレースバックになったり、小数リテラルが無言で `inf` になっていた問題を修正（構文エラー「数値が大きすぎます」として表示）
- 🐛 深すぎる入れ子で英語の `maximum recursion depth exceeded` が表示されていた問題を修正（日本語メッセージで表示）
- 🐛 `scripts/verify.py` が venv 未アクティブ時に `FileNotFoundError: ruff` で失敗する不具合を修正
- 🔧 開発依存関係に `build` を追加し、`pip install -e ".[dev]"` だけで `scripts/verify.py` が完走するようにした
- 🔗 README のアーキテクチャ文書へのリンク切れ（`docs/ARCHITECTURE.md` → `ARCHITECTURE.md`）を修正

変更時は `Added`、`Changed`、`Fixed`、`Security` のいずれかで追記してください。
