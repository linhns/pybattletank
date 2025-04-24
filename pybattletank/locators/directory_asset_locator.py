import os
import pathlib
from typing import Union

from .asset_locator import AssetLocator


class DirectoryAssetLocator(AssetLocator):
    def __init__(self, root_dir: Union[str, pathlib.Path]) -> None:
        self.root_dir = pathlib.Path(root_dir)

    def locate(self, name: str) -> Union[str, os.PathLike]:
        path = self.root_dir / name
        return path
