"""パッケージのバージョン取得を検証するテスト。"""

import importlib
from importlib.metadata import PackageNotFoundError
from unittest import mock

import asl


def test_version_falls_back_when_package_not_installed():
    with mock.patch(
        "importlib.metadata.version",
        side_effect=PackageNotFoundError("aurora-sauce-language"),
    ):
        importlib.reload(asl)
        assert asl.__version__ == "0.1.0.dev0"

    # 後続のテストに影響しないよう、通常の状態へ戻す。
    importlib.reload(asl)
    assert asl.__version__ == "0.1.0.dev0"
