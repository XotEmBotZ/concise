import tomllib
from typing import Any
import psycopg

def load_config(filename:str)-> dict[str,Any]:
    return tomllib.load(open(filename,'rb'))
