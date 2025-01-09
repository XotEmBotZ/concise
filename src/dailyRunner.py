import os

# abspath = os.path.abspath(__file__)
# dname = os.path.dirname(abspath)
# os.chdir(dname)

from concise.utils.classes import Main  # noqa: E402
from concise.utils.utils import load_config  # noqa: E402

if __name__ == "__main__":
    Main(load_config("config.toml")).d1_goal()
