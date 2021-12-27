import logging
import typing

from flask import render_template

import api
import api_types
from soda_api import client, LICENSE_DATASET


log = logging.getLogger(__name__)


def license_lookup(license: str) -> str:
    if license:
        try:
            results = client.get(
                LICENSE_DATASET, limit=1, where=f"license like '{license.upper()}'"
            )
            if not results:
                html = (
                    # Disable reason: No need to fix line length for strings
                    "<p><b>No vehicle found for this license in public dataset</b>"
                    "</p><p>(not all undercover vehicles have available information)</p>"
                )
            else:
                r = results[0]
                html = render_template("license.html", **r)

        except Exception as err:
            log.exception(err)
            html = f"<p><b>Error:</b> {err}"

        log.info("Final HTML:\n{}".format(html))
        return html

    else:
        return ""


def filter_records(
    records: typing.List[api_types.Record],
) -> typing.List[api_types.Record]:
    filtered: typing.List[api_types.Record] = []
    for idx, record in enumerate(records):
        next_idx = idx + 1
        if next_idx == len(records):
            # Reached the end of the list
            break
        next_record = records[next_idx]
        # Override date keys so they're the same for all comparisons
        if {**record, "date": True} != {**next_record, "date": True}:  # type: ignore
            filtered.append(record)
    return filtered


def name_lookup(
    metadata: api_types.DatasetMetadata,
    entities: typing.List[api_types.Entity],
    strict_search: bool = None,
    historical: bool = False,
    show_full_history: bool = False,
    **kwargs,
) -> typing.Tuple[str, bool]:
    if strict_search is None:
        strict_search = True
        for fuzzy_entity in [entity for entity in entities if entity["is_fuzzy"]]:
            if (
                fuzzy_entity["query_param"] in kwargs
                and kwargs[fuzzy_entity["query_param"]] != ""
            ):
                strict_search = False
                break

    try:
        records = api.get_results(metadata, strict_search, historical, **kwargs)
        if not show_full_history and historical:
            records = filter_records(records or [])
        html = (
            api.render_historical_officers(records, metadata)
            if historical
            else api.render_officers(records, metadata)
        )
    except Exception as err:
        log.exception(err)
        html = f"<p><b>Error:</b> {err}"

    log.info("Final HTML:\n{}".format(html))
    return html, strict_search
