from csv import DictReader
from decimal import Decimal
from pathlib import Path
from typing import Dict

from flask import render_template
from sodapy import Socrata


# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
LICENSE_DATASET = "enxu-fgzb"
SALARY_DATASET = "2khk-5ukd"
BADGE_DATASET_PATH = Path(__file__).parent / "data" / "spd-badges.csv"


def _data() -> Dict[str, Dict[str, str]]:
    """Set up initial dataset"""
    print("Loading initial badge data")
    data = {}
    with BADGE_DATASET_PATH.open("r") as file:
        reader = DictReader(file)
        for row in reader:
            data[row["Serial"]] = row

    return data


BADGE_DATASET = _data()


def license_lookup(license: str) -> str:
    try:
        results = client.get(
            LICENSE_DATASET, limit=1, where=f"license='{license.upper()}'"
        )
        if not results:
            html = "<p><b>No vehicle found for this license</b></p>"
        else:
            r = results[0]
            html = render_template("license.j2", **r)

    except Exception as err:
        print(f"Error: {err}")
        html = f"<p><b>Error:</b> {err}"

    print("Final HTML:\n{}".format(html))
    return html


def _augment_with_salary(record: Dict[str, str]) -> Dict[str, str]:
    first = record["FirstName"]
    last = record["Surname"]
    middle = record["MiddleInitMostly"]
    if middle:
        name = f"{first} {middle} {last}"
    else:
        name = f"{first} {last}"
    context = {**record, "name": name}

    results = client.get(
        SALARY_DATASET,
                limit=1,
                where=f"department='Police Department' AND last_name='{last}' AND first_name='{first}'",
    )
    if results:
        s = results[0]
        projected = Decimal(s["hourly_rate"]) * 40 * 50
        # Format with commas
        context = {**context, **s, "projected": f"{projected:,}"}

    return context


def badge_lookup(badge: str) -> str:
    try:
        r = BADGE_DATASET.get(badge)
        if not r:
            html = "<p><b>No officer found for this badge number</b></p>"
        else:
            context = _augment_with_salary(r)
            html = render_template("badge.j2", **context)

    except Exception as err:
        print(f"Error: {err}")
        html = f"<p><b>Error:</b> {err}"

    print("Final HTML:\n{}".format(html))
    return html
