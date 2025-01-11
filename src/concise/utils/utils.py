from typing import Any

import toml


def load_config(filename: str) -> dict[str, Any]:
    with open(filename, "r") as f:
        return toml.load(f)


def dump_config(config: dict, filename: str) -> str:
    with open(filename, "w") as f:
        return toml.dump(config, f)
