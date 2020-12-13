from decimal import Decimal
from typing import Dict, Tuple, List, Optional, Any

from flask import render_template
from sodapy import Socrata
import sqlite3


# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
LICENSE_DATASET = "enxu-fgzb"
SALARY_DATASET = "2khk-5ukd"

# Connect to SQL database
sql_conn = sqlite3.connect('./data/1-312-data.db')
sql_curs = sql_conn.cursor()


def license_lookup(license: str) -> str:
    if license:
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

    else:
        return ""


def _augment_with_salary(record: Tuple) -> Dict[str, str]:
    # The tuple positions are following the database schema
    first = record[1]
    last = record[3]
    middle = record[2]
    if middle:
        name = f"{first} {middle} {last}"
    else:
        name = f"{first} {last}"
    context = {
        "name": name,
        "title": record[4],
        "unit": record[5],
        "serial": record[0],
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


def _sort_names(record: List[Tuple]) -> Tuple:
    for r in sorted(record, key=lambda x: x[3]):
        yield r


def name_lookup(last_name: Any, first_name: Any, badge: Any) -> str:
    if last_name or first_name or badge:
        try:
            records = sql_curs.execute(
                "SELECT * FROM officers WHERE Last = ? OR First = ? OR Serial = ?",
                (last_name, first_name, badge),
            ).fetchall()
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

    else:
        return ""
