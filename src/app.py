#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from sodapy import Socrata

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, static_folder="public", template_folder="views")

# Set up the sodapy client
client = Socrata("data.seattle.gov", None)
DATASET = "enxu-fgzb"


@app.route("/")
def homepage():
    """Displays the homepage."""
    return render_template("index.html")


@app.route("/license-lookup", methods=["POST"])
def lookup():
    """Simple API endpoint for dreams.
    In memory, ephemeral, like real dreams.
    """

    html = ""
    # Add a dream to the in-memory database, if given.
    if "license" in request.args:
        license = request.args["license"]
        try:
            results = client.get(DATASET, limit=1, where=f"license='{license.upper()}'")
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


if __name__ == "__main__":
    app.run()
