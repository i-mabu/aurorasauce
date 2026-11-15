"""Aurora Sauce Language のパッケージ。"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aurora-sauce-language")
except PackageNotFoundError:  # ソースツリーから直接実行する場合
    __version__ = "0.1.0.dev0"

__all__ = ["__version__"]
