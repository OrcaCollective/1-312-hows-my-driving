import sys

from typing import List, Dict

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class SearchRoute(TypedDict):
    path: str
    query_params: List[str]


class FieldMetadata(TypedDict):
    FieldName: str
    Label: str


class DatasetMetadata(TypedDict):
    id: str
    name: str
    last_available_roster_date: str
    fields: List[FieldMetadata]
    search_routes: Dict[str, SearchRoute]


class Record(TypedDict, total=False):
    first_name: str
    last_name: str


class Entity(TypedDict):
    entity_name: str
    query_param: str
    fuzzy: bool


DEFAULT_DATASET = "spd"
