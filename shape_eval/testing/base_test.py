import json
from types import SimpleNamespace
from .civitai_sample import civitai_str

def json_to_obj(json_str):
    return json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

def get_civitai_sample():
    return json_to_obj(civitai_str)
