from decimal import Decimal
from functools import lru_cache
from typing import Dict, Callable, Optional

from flask import render_template
from soda_api import client, SALARY_DATASET
from api_types import Record, DEFAULT_DATASET


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
    return render_template("seattle_extras.j2", **context)


def augment_with_salary(record: Record) -> str:
    last = record["last_name"]
    first = record["first_name"]
    return _augment_with_salary_cached(last, first)


EXTRAS_MAPPING: Dict[str, Callable[[Record], str]] = {
    DEFAULT_DATASET: augment_with_salary,
}
