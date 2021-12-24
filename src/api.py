import logging
from typing import List, Mapping, Optional

import cachetools
import requests
from flask import render_template

from extras import EXTRAS_MAPPING
from api_types import DatasetMetadata, Record, Entity


log = logging.getLogger(__name__)


# Data API configuration
DATA_API_HOST = "https://1312api.tech-bloc-sea.dev"

# Cache
DatasetMapping = Mapping[str, DatasetMetadata]
DATASET_CACHE: cachetools.TTLCache = cachetools.TTLCache(1000, 300)


def get_datasets() -> DatasetMapping:
    if DATASET_CACHE.currsize == 0:
        log.info("Refreshing dataset cache")
        datasets: List[DatasetMetadata] = requests.get(
            f"{DATA_API_HOST}/departments"
        ).json()
        for dataset in datasets:
            DATASET_CACHE[dataset["id"]] = dataset
    return DATASET_CACHE


def get_results(
    metadata: DatasetMetadata, strict_search: bool, historical: bool = False, **kwargs
) -> Optional[List[Record]]:
    route_key = "fuzzy"
    if historical:
        route_key = "historical-exact"
    elif strict_search:
        route_key = "exact"
    route = metadata["search_routes"][route_key]
    search_path = route["path"]
    query_params = route["query_params"]
    url = DATA_API_HOST + search_path + "?"
    params = []
    values = []
    for query_param in query_params:
        value = kwargs.get(query_param)
        if value is None:
            continue
        values.append(value)
        params.append(f"{query_param}={value}")
    url += "&".join(params)
    print(url)

    if not values or all(value is None for value in values):
        return None

    response = requests.get(url)
    if response.status_code != 200:
        if response.text:
            msg = response.text
        else:
            msg = f"unexpected status code {response.status_code} when accessing {url}"
        raise Exception(msg)
    records = response.json()
    return records


def get_query_fields(metadata: Optional[DatasetMetadata]) -> List[Entity]:
    if metadata is None:
        return []

    search_routes = metadata["search_routes"]
    fields = metadata["fields"]
    exact_params = set(search_routes["exact"]["query_params"])
    fuzzy_params = set(search_routes["fuzzy"]["query_params"])
    # Remove fuzzy params from exact ones
    exact_params -= fuzzy_params
    entities: List[Entity] = []
    for param in [*sorted(exact_params), *sorted(fuzzy_params)]:
        name = "Name Unknown"
        for field in fields:
            if param == field["FieldName"]:
                name = field["Label"]
                break
        is_fuzzy = False
        if param in fuzzy_params:
            is_fuzzy = True
            name += " (fuzzy)"
        entities.append(
            {"entity_name": name, "query_param": param, "is_fuzzy": is_fuzzy}
        )
    return entities


def render_officers(records: Optional[List[Record]], metadata: DatasetMetadata) -> str:
    if records is None:
        return ""
    if len(records) == 0:
        return "<p><b>No officers found</b></p>"
    htmls = []
    for record in records:
        extras = ""
        if metadata["id"] in EXTRAS_MAPPING:
            extras = EXTRAS_MAPPING[metadata["id"]](record)
        htmls.append(
            render_template(
                "officer.html",
                record=record,
                metadata=metadata,
                extras=extras,
                historical_available="historical-exact" in metadata["search_routes"],
            )
        )
    html = "\n<br/>\n".join(htmls)
    log.debug(f"Final HTML: {html}")
    return html


FIELDS_NOT_TO_RENDER = {
    "first_name",
    "middle_name",
    "last_name",
}


def render_historical_officers(
    records: Optional[List[Record]], metadata: DatasetMetadata, show_full_history: bool
) -> str:
    if records is None:
        return ""
    if len(records) == 0:
        return "<p><b>No historical record found for this badge</b></p>"

    return render_template(
        "officer-table.html",
        records=records,
        fields=[
            field
            for field in metadata["fields"]
            if field["FieldName"] not in FIELDS_NOT_TO_RENDER
        ],
        show_full_history=show_full_history,
    )
