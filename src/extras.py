import csv
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Dict, Callable, Optional

from flask import render_template
from soda_api import client, SALARY_DATASET
from api_types import Record, DEFAULT_DATASET


OO_ID_MAPPING = {}
OO_URL = "https://spd.watch/officer/{id_}"
OO_MAPPING_PATH = Path(__file__).parent / "data" / "badge-oo-id-mapping.csv"


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
    return render_template("extras/seattle_salary.html", **context)


def augment_with_salary(record: Record) -> str:
    if not record["is_current"]:
        return ""

    last = record["last_name"]
    first = record["first_name"]
    return _augment_with_salary_cached(last, first)


########################################################################################
# OpenOversight ID mapping
########################################################################################
def _load_oo_id_mapping() -> None:
    with OO_MAPPING_PATH.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        # Do this rather than a dict comprehension so we populate the global object
        for row in reader:
            OO_ID_MAPPING[row["badge number"]] = row["id"]


def augment_with_oo_link(record: Record) -> str:
    if not OO_ID_MAPPING:
        _load_oo_id_mapping()
    if oo_id := OO_ID_MAPPING.get(record["badge"]):  # type: ignore
        oo_link = OO_URL.format(id_=oo_id)
        return render_template("extras/seattle_oo_id.html", oo_link=oo_link)
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
