#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template

import dataset


app = Flask(__name__, static_folder="public", template_folder="views")


################################################################################
# Licenses
################################################################################
LICENSE_CONTEXT = {
    "title": "Seattle Public Vehicle Lookup",
    "entity_name_long": "license plate",
    "entity_name_short": "License #",
    "data_source": "https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb",
    "lookup_url": "license-lookup",
}


@app.route("/")
def license_page():
    """Displays the homepage."""
    return render_template("index.html", **LICENSE_CONTEXT)


@app.route("/license-lookup/<license>")
def license_lookup(license):
    html = dataset.license_lookup(license)
    return render_template("index.html", **LICENSE_CONTEXT, entity_html=html)


################################################################################
# Badges
################################################################################
BADGE_CONTEXT = {
    "title": "Seattle Officer Badge Lookup",
    "entity_name_long": "badge number",
    "entity_name_short": "Badge #",
    "data_source": "https://data.seattle.gov/City-Business/City-of-Seattle-Wage-Data/2khk-5ukd",
    "lookup_url": "badge-lookup",
}


@app.route("/badge")
def badge_page():
    return render_template("index.html", **BADGE_CONTEXT)


@app.route("/badge-lookup/<badge>")
def badge_lookup(badge):
    html = dataset.badge_lookup(badge)
    return render_template("index.html", **BADGE_CONTEXT, entity_html=html)


################################################################################
# Names
################################################################################
NAME_CONTEXT = {
    "title": "Seattle Officer Name Lookup",
    "entity_name_long": "last name",
    "entity_name_short": "Lastname",
    "data_source": "https://data.seattle.gov/City-Business/City-of-Seattle-Wage-Data/2khk-5ukd",
    "lookup_url": "name-lookup",
}


@app.route("/name")
def name_page():
    return render_template("index.html", **NAME_CONTEXT)


@app.route("/name-lookup/<name>")
def name_lookup(name):
    html = dataset.name_lookup(name)
    return render_template("index.html", **NAME_CONTEXT, entity_html=html)


if __name__ == "__main__":
    app.run()
