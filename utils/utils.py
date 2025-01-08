from typing import Any

import tomllib


def load_config(filename: str) -> dict[str, Any]:
    return tomllib.load(open(filename, "rb"))
