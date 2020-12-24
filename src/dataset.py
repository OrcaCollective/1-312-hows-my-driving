from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple, List, NamedTuple, Generator

from flask import render_template
from sodapy import Socrata
import sqlite3
import requests


#################################################################################
# ./data/1-312-data.db Database format
#################################################################################
# Example:
# Table
# - column (datatype)
#################################################################################
# officers
# - Serial (string)
# - First (string)
# - Middle (string)
# - Last (string)
# - TitleDescription (string)
# - UnitDescription (string)
#################################################################################


# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
LICENSE_DATASET = "enxu-fgzb"
SALARY_DATASET = "2khk-5ukd"
DATA_API_HOST = "https://spd-lookup.herokuapp.com"


class RosterRecord(NamedTuple):
    serial: int
    first: str
    middle: str
    last: str
    title: str
    unit: str


def ping_data_api() -> int:
    response = requests.Get(f"{DATA_API_HOST}/ping")
    return response.status_code


def _sort_names(records: List[Tuple]) -> Generator[RosterRecord, None, None]:
    # Convert to named tuples
    records = [RosterRecord(*r) for r in records]
    for r in sorted(records, key=lambda x: x.last):
        yield r


def license_lookup(license: str) -> str:
    if license:
        try:
            results = client.get(
                LICENSE_DATASET, limit=1, where=f"license like '{license.upper()}'"
            )
            if not results:
                html = (
                    "<p><b>No vehicle found for this license in public dataset</b>"
                    "</p><p>(not all undercover vehicles have available information)</p>"
                )
            else:
                r = results[0]
                html = render_template("license.j2", **r)

        except Exception as err:
            print(f"Error: {err}")
            html = f"<p><b>Error:</b> {err}"

        print("Final HTML:\n{}".format(html))
        return html

    else:
        return ""


def _augment_with_salary(record: RosterRecord) -> Dict[str, str]:
    # The tuple positions are following the database schema
    if record.middle:
        name = f"{record.first} {record.middle} {record.last}"
    else:
        name = f"{record.first} {record.last}"
    context = {
        "name": name,
        "title": record.title,
        "unit": record.unit,
        "serial": record.serial,
    }

    results = client.get(
        SALARY_DATASET,
        limit=1,
        where=f"last_name='{record.last}' AND first_name='{record.first}'",
    )
    if results:
        s = results[0]
        projected = Decimal(s["hourly_rate"]) * 40 * 50
        # Format with commas
        context = {**context, **s, "projected": f"{projected:,}"}

    return context


def name_lookup(first_name: str, last_name: str, badge: str) -> str:
    if not (first_name or last_name or badge):
        return ""
    else:
        try:
            records = []
            if not badge:
                url = f"{DATA_API_HOST}/officer/search?first_name={first_name}&last_name={last_name}"
            else:
                url = f"{DATA_API_HOST}/officer?badge={badge}"
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception(
                    f"unexpected status code {response.status_code} when accessing {url}"
                )
            records = response.json()
            if len(records) == 0:
                html = "<p><b>No officer found for this name</b></p>"
            else:
                htmls = []
                for r in records:
                    context = _augment_with_salary(
                        RosterRecord(
                            r.get("badge_number"),
                            r.get("first_name"),
                            r.get("middle_name"),
                            r.get("last_name"),
                            r.get("title"),
                            r.get("unit"),
                        )
                    )
                    htmls.append(render_template("officer.j2", **context))
                html = "\n<br/>\n".join(htmls)

        except Exception as err:
            print(f"Error: {err}")
            html = f"<p><b>Error:</b> {err}"

        print("Final HTML:\n{}".format(html))
        return html
