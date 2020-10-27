#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template

import dataset


app = Flask(__name__, static_folder="public", template_folder="views")


################################################################################
# Licenses
################################################################################
@app.route("/")
def license_page():
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
    license = request.args.get("entity", "")
    html = dataset.license_lookup(license)
    # Return the list of remembered dreams.
    return html


################################################################################
# Badges
################################################################################
@app.route("/badge")
def badge_page():
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
    badge = request.args.get("entity")
    html = dataset.badge_lookup(badge)
    # Return the list of remembered dreams.
    return html


if __name__ == "__main__":
    app.run()
