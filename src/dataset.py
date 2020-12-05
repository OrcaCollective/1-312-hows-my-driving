from collections import defaultdict
from csv import DictReader
from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple

from flask import render_template
from sodapy import Socrata


# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
LICENSE_DATASET = "enxu-fgzb"
SALARY_DATASET = "2khk-5ukd"
BADGE_DATASET_PATH = Path(__file__).parent / "data" / "SPD_roster_11-15-20.csv"
_DataDict = Dict[str, Dict[str, str]]
_DataNameLookup = Dict[str, _DataDict]


class C:
    """Columns"""

    SERIAL = "Serial"
    FIRST = "First"
    MIDDLE = "Middle"
    LAST = "Last"
    TITLE = "Title Description"
    UNIT = "Unit Description"

    fields = [SERIAL, FIRST, MIDDLE, LAST, TITLE, UNIT]


def _data() -> Tuple[_DataDict, _DataNameLookup]:
    """Set up initial dataset"""
    print("Loading initial badge data")
    badges = {}
    names = defaultdict(dict)
    with BADGE_DATASET_PATH.open("r") as file:
        reader = DictReader(file)
        for row in reader:
            r = {k: row[k] for k in C.fields}
            badges[row[C.SERIAL]] = r
            # There may be numerous rows per unique name, so this makes them
            # easiest to index appropriately/overwrite with the most current value
            names[row[C.LAST]][row[C.SERIAL]] = r

    return badges, names


BADGE_DATASET, NAME_DATASET = _data()


def license_lookup(license: str) -> str:
    try:
        results = client.get(
            LICENSE_DATASET, limit=1, where=f"license='{license.upper()}'"
        )
        if not results:
            html = "<p><b>No vehicle found for this license in public dataset</b></p><p>(not all undercover vehicles have available information)</p>"
        else:
            r = results[0]
            html = render_template("license.j2", **r)

    except Exception as err:
        print(f"Error: {err}")
        html = f"<p><b>Error:</b> {err}"

    print("Final HTML:\n{}".format(html))
    return html


def _augment_with_salary(record: Dict[str, str]) -> Dict[str, str]:
    first = record[C.FIRST]
    last = record[C.LAST]
    middle = record[C.MIDDLE]
    if middle:
        name = f"{first} {middle} {last}"
    else:
        name = f"{first} {last}"
    context = {
        "name": name,
        "title": record[C.TITLE],
        "unit": record[C.UNIT],
        "serial": record[C.SERIAL],
    }

    results = client.get(
        SALARY_DATASET,
        limit=1,
        where=f"last_name='{last}' AND first_name='{first}'",
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
            html = render_template("officer.j2", **context)

    except Exception as err:
        print(f"Error: {err}")
        html = f"<p><b>Error:</b> {err}"

    print("Final HTML:\n{}".format(html))
    return html


def _sort_names(record: _DataDict):
    for r in sorted(record.values(), key=lambda x: x[C.FIRST]):
        yield r


def name_lookup(name: str) -> str:
    try:
        records = NAME_DATASET.get(name)
        if not records:
            html = "<p><b>No officer found for this name</b></p>"
        else:
            htmls = []
            for r in _sort_names(records):
                context = _augment_with_salary(r)
                htmls.append(render_template("officer.j2", **context))
            html = "\n<br/>\n".join(htmls)

    except Exception as err:
        print(f"Error: {err}")
        html = f"<p><b>Error:</b> {err}"

    print("Final HTML:\n{}".format(html))
    return html
