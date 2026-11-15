# 🗺️ ロードマップ

## ✅ Phase 0: 管理基盤

- README と開発文書
- CI の再現可能な検証
- Windows / PowerShell を含む手順
- セキュリティとリリース方針

## ✅ Phase 1: 品質強化

- カバレッジ計測（下限 90%、2026-11-14 時点で 98.9%）と E2E
- 依存関係監査を `scripts/verify.py` と CI 経路に組み込み（監査は毎回の検証で実行）
- エラー境界の改善：CLI が日本語メッセージ＋終了コードでエラーを返す
- `scripts/verify.py` の修正：venv 未アクティブでも ruff / pip-audit が動く

## 📈 Phase 2: 機能拡張

設計は [Phase 2 設計文書](PHASE2_DESIGN.md) を参照。

- ✅ 2a：材料と分量（変数・数値・四則演算・文字列結合）
- ✅ 2b：味見（`if` / `else`、比較演算・真偽値）
- ✅ 2c：繰り返し（`repeat N { }`）
- 🔜 2d：レシピ（関数定義・呼び出し・引数・`serve`）
- ⏭️ 2e：対話（`ask` / `asl repl`）は Phase 3 へ

大きな変更は ADR とテストを先に作成します。
