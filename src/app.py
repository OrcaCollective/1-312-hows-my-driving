#!/usr/bin/env python
# -*- coding: utf-8 -*-
from csv import DictReader
from decimal import Decimal
from pathlib import Path
from typing import Dict

from flask import Flask, request, render_template
from sodapy import Socrata

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, static_folder="public", template_folder="views")

# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
LICENSE_DATASET = "enxu-fgzb"
SALARY_DATASET = "2khk-5ukd"
BADGE_DATASET_PATH = Path(__file__).parent / "data" / "spd-badges.csv"


# Set up dataset
def _data() -> Dict[str, Dict[str, str]]:
    print("Loading initial badge data")
    data = {}
    with BADGE_DATASET_PATH.open("r") as file:
        reader = DictReader(file)
        for row in reader:
            data[row["Serial"]] = row

    return data


BADGE_DATASET = _data()


################################################################################
# Licenses
################################################################################
@app.route("/")
def homepage():
    """Displays the homepage."""
    context = {
        "title": "Seattle Public Vehicle Lookup",
        "entity_name_long": "license plate",
        "entity_name_short": "License #",
        "entity": "license",
        "data_source": "https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb",
        "lookup_url": "license-lookup"
    }
    return render_template("index.html", **context)


@app.route("/license-lookup", methods=["POST"])
def license_lookup():
    """Simple API endpoint for dreams.
    In memory, ephemeral, like real dreams.
    """

    html = ""
    # Add a dream to the in-memory database, if given.
    if "entity" in request.args:
        license = request.args["entity"]
        try:
            results = client.get(
                LICENSE_DATASET, limit=1, where=f"license='{license.upper()}'"
            )
            if not results:
                html = "<p><b>No vehicle found for this license</b></p>"
            else:
                r = results[0]
                html = f"""
<p><b>License:</b> {r['license']}</p>
<p><b>Make:</b> {r['make']}</p>
<p><b>Model:</b> {r['model']}</p>
<p><b>Department:</b> {r['dept']}</p>
<p><b>Description:</b> {r['descrip']}</p>
<p><b>Equipment Type:</b> {r['equipment_type']}</p>
"""

        except Exception as err:
            print(f"Error: {err}")
            html = f"<p><b>Error:</b> {err}"
        print("Final HTML:\n{}".format(html))

    # Return the list of remembered dreams.
    return html


################################################################################
# Badges
################################################################################
@app.route("/badge")
def badge():
    context = {
        "title": "Seattle Officer Badge Lookup",
        "entity_name_long": "badge number",
        "entity_name_short": "Badge #",
        "entity": "badge",
        "data_source": "https://data.seattle.gov/City-Business/City-of-Seattle-Wage-Data/2khk-5ukd",
        "lookup_url": "badge-lookup"
    }
    return render_template("index.html", **context)


@app.route("/badge-lookup", methods=["POST"])
def badge_lookup():
    html = ""
    if "entity" in request.args:
        badge = request.args["entity"]
        try:
            r = BADGE_DATASET.get(badge)
            if not r:
                html = "<p><b>No officer found for this badge number</b></p>"
            else:
                first = r["FirstName"]
                last = r["Surname"]
                middle = r["MiddleInitMostly"]
                if middle:
                    name = f"{first} {middle} {last}"
                else:
                    name = f"{first} {last}"
                html = f"""
<p><b>Badge #:</b> {r['Serial']}</p>
<p><b>Name:</b> {name}</p>
<p><b>Rank:</b> {r['RankRole']}</p>
"""
                results = client.get(
                    SALARY_DATASET,
                    limit=1,
                    where=f"department='Police Department' AND last_name='{last}' AND first_name='{first}'",
                )
                if results:
                    s = results[0]
                    projected = Decimal(s["hourly_rate"]) * 40 * 50
                    html += f"""
<p><b>Job Title:</b> {s['job_title']}</p>
<p><b>Hourly Rate:</b> ${s['hourly_rate']}</p>
<p><b>Projected salary (w/o overtime):</b> ${projected:,}</p>
"""

        except Exception as err:
            print(f"Error: {err}")
            html = f"<p><b>Error:</b> {err}"
        print("Final HTML:\n{}".format(html))

    # Return the list of remembered dreams.
    return html


if __name__ == "__main__":
    app.run()
