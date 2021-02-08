from typing import TypedDict, List, Dict


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


DEFAULT_DATASET = "spd"
