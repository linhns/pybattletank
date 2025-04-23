import importlib
import os
from importlib.resources import Package
from typing import Union

from .asset_locator import AssetLocator


class PackagedAssetLocator(AssetLocator):
    def __init__(self, anchor: Package) -> None:
        self.traversable = importlib.resources.files(anchor)

    def locate(self, name: str) -> Union[str, os.PathLike]:
        with importlib.resources.as_file(self.traversable.joinpath(name)) as path:
            fp = path.resolve()
        return fp
