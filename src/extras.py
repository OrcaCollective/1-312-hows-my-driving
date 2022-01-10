import csv
import io
import logging
from decimal import Decimal
from functools import lru_cache
from typing import Dict, Callable, Optional, Mapping

import cachetools
import requests
from flask import render_template
from soda_api import client, SALARY_DATASET
from api_types import Record, DEFAULT_DATASET


log = logging.getLogger(__name__)


OO_ID_MAPPING: Dict[str, str] = {}
OO_ID_SOURCE_URL = (
    "https://openoversight.tech-bloc-sea.dev/download/department/1/officers"
)
OO_URL_TEMPLATE = "https://spd.watch/officer/{id_}"
OO_CACHE: cachetools.TTLCache = cachetools.TTLCache(maxsize=10_000, ttl=3600 * 24)


########################################################################################
# Salary data
########################################################################################
@lru_cache(maxsize=1000)
def _augment_with_salary_cached(last: Optional[str], first: Optional[str]) -> str:
    """Cached augmentation for faster retrieval."""
    results = client.get(
        SALARY_DATASET,
        limit=1,
        where=f'last_name="{last}" AND first_name="{first}"',
    )
    if not results:
        return ""
    s = results[0]
    projected = Decimal(s["hourly_rate"]) * 40 * 50
    # Format with commas
    context = {**s, "projected": f"{projected:,}"}
    return render_template("extras/seattle-salary.html", **context)


def augment_with_salary(record: Record) -> str:
    if not record["is_current"]:
        return ""

    last = record["last_name"]
    first = record["first_name"]
    return _augment_with_salary_cached(last, first)


########################################################################################
# OpenOversight ID mapping
########################################################################################
def _get_oo_id_mapping() -> Mapping[str, str]:
    if OO_CACHE.currsize == 0:
        log.info("Refreshing OO ID cache")
        try:
            response = requests.get(OO_ID_SOURCE_URL, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            log.warning(f"OO ID URL {OO_ID_SOURCE_URL} failed with error: {err}")
            return {}
        reader = csv.DictReader(io.StringIO(response.text, newline=""))
        for row in reader:
            OO_CACHE[row["badge number"]] = row["id"]
    return OO_CACHE


def augment_with_oo_link(record: Record) -> str:
    id_mapping = _get_oo_id_mapping()
    if oo_id := id_mapping.get(record["badge"]):  # type: ignore
        oo_link = OO_URL_TEMPLATE.format(id_=oo_id)
        return render_template("extras/seattle-oo-id.html", oo_link=oo_link)

    return ""


########################################################################################
# Extras proxy
########################################################################################
def seattle_augment(record: Record) -> str:
    salary = augment_with_salary(record)
    oo_link = augment_with_oo_link(record)
    return salary + "\n" + oo_link


EXTRAS_MAPPING: Dict[str, Callable[[Record], str]] = {
    DEFAULT_DATASET: seattle_augment,
}
