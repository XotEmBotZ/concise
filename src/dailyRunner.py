import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

from utils.classes import Main  # noqa: E402
from utils.utils import load_config  # noqa: E402

if __name__ == "__main__":
    print("In DaillyRunner...")
    # Main(load_config("config.toml"))
    Main(load_config("config.toml")).d1_goal()
