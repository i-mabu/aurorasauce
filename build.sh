#!/usr/bin/env bash
# aurorasauce (Aurora Sauce Language) のフルビルドを 1 コマンドで行うスクリプト。
# 依存関係のインストール → 一括検証 (テスト・Lint・依存関係監査・ビルド) を
# 順に実行し、失敗したステップで即座に止まって、どのステップで落ちたかを表示する。
# 検証は repo 標準の scripts/verify.py を使う。依存関係は README の手順どおり
# repo 直下の .venv に入れる (.venv は .gitignore 対象)。

# ===== 1. 準備 =====
set -euo pipefail
cd "$(dirname "$0")"

step() {
  echo
  echo "===== $1 ====="
}

fail() {
  echo "ERROR: ステップが失敗しました: $1" >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || fail "前提チェック (Python 3 が見つかりません)"

# ===== 2. 依存関係のインストール =====
step "1/2 依存関係のインストール"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv || fail "依存関係のインストール (.venv の作成)"
fi
.venv/bin/python -m pip install -e ".[dev]" || fail "依存関係のインストール (pip install -e \".[dev]\")"

# ===== 3. 一括検証 (テスト・Lint・依存関係監査・ビルド) =====
step "2/2 一括検証 (scripts/verify.py)"
.venv/bin/python scripts/verify.py || fail "一括検証 (scripts/verify.py)"

# ===== 4. 完了 =====
echo
echo "BUILD OK: aurorasauce のテスト・Lint・ビルドがすべて成功しました (成果物: dist/)"
