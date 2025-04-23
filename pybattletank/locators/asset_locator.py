import os
from typing import Union


class AssetLocator:
    def locate(self, name: str) -> Union[str, os.PathLike]:
        raise NotImplementedError()
