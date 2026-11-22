@echo off
rem aurorasauce (Aurora Sauce Language) のフルビルドを 1 コマンドで行うスクリプト (Windows 用)。
rem 依存関係のインストール → 一括検証 (テスト・Lint・依存関係監査・ビルド) を
rem 順に実行し、失敗したステップで即座に止まって、どのステップで落ちたかを表示する。
rem 検証は repo 標準の scripts/verify.py を使う。依存関係は README の手順どおり
rem repo 直下の .venv に入れる (.venv は .gitignore 対象)。
setlocal
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python が見つかりません。Python 3.11 以上をインストールしてください。 1>&2
  exit /b 1
)

echo.
echo ===== 1/2 依存関係のインストール =====
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 goto fail_venv
)
.venv\Scripts\python.exe -m pip install -e ".[dev]"
if errorlevel 1 goto fail_install

echo.
echo ===== 2/2 一括検証 (scripts/verify.py) =====
.venv\Scripts\python.exe scripts\verify.py
if errorlevel 1 goto fail_verify

echo.
echo BUILD OK: aurorasauce のテスト・Lint・ビルドがすべて成功しました (成果物: dist\)
exit /b 0

:fail_venv
echo ERROR: ステップが失敗しました: 依存関係のインストール (.venv の作成) 1>&2
exit /b 1

:fail_install
echo ERROR: ステップが失敗しました: 依存関係のインストール (pip install -e ".[dev]") 1>&2
exit /b 1

:fail_verify
echo ERROR: ステップが失敗しました: 一括検証 (scripts/verify.py) 1>&2
exit /b 1
