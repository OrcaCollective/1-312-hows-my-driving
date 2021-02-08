from decimal import Decimal
from typing import Dict, Callable

from flask import render_template
from soda_api import client, SALARY_DATASET
from api_types import Record, DEFAULT_DATASET


def _augment_with_salary(record: Record) -> str:
    last = record["last_name"]
    first = record["first_name"]
    results = client.get(
        SALARY_DATASET,
        limit=1,
        where=f'last_name="{last}" AND first_name="{first}"',
    )
    if results:
        s = results[0]
        projected = Decimal(s["hourly_rate"]) * 40 * 50
        # Format with commas
        context = {**s, "projected": f"{projected:,}"}
        return render_template("seattle_extras.j2", **context)


EXTRAS_MAPPING: Dict[str, Callable[[Record], str]] = {
    DEFAULT_DATASET: _augment_with_salary,
}
