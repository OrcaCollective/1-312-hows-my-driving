from decimal import Decimal
from typing import Dict, Tuple, List, NamedTuple, Generator

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

#################################################################################
# Database format
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


class RosterRecord(NamedTuple):
    serial: int
    first:  str
    last:   str
    middle: str
    title:  str
    unit:   str


def _sort_names(records: List[Tuple]) -> Generator[RosterRecord, None, None]:
    # Convert to named tuples
    records = [RosterRecord(*r) for r in records]
    for r in sorted(records, key=lambda x: x.last):
        yield r


def license_lookup(license: str) -> str:
    if license:
        try:
            results = client.get(
                LICENSE_DATASET, limit=1, where=f"license='{license.upper()}'"
            )
            if not results:
                html = "<p><b>No vehicle found for this license in public dataset</b>" \
                       "</p><p>(not all undercover vehicles have available information)</p>"
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


def _build_sql_query(queries: List[Tuple]) -> Tuple[str, List[str]]:
    query_statements = []
    parameters = []
    for field, operator, value in queries:
        if not value:
            continue
        query_statements.append(f"{field} {operator} ?")
        parameters.append(value)
    return " AND ".join(query_statements), parameters


def name_lookup(first_name: str, last_name: str, badge: str) -> str:
    if not (first_name or last_name or badge):
        return ""
    else:
        base_sql_query = "SELECT * FROM officers WHERE "
        queries_list = [
            ("First", "LIKE", first_name),
            ("Last", "LIKE", last_name),
            ("Serial", "=", badge)
        ]
        filter_sql_query, query_tuple = _build_sql_query(queries_list)
        sql_query = base_sql_query + filter_sql_query
        try:
            records = sql_curs.execute(sql_query, query_tuple,).fetchall()
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
