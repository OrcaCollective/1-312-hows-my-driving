#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for

import dataset


app = Flask(__name__, static_folder="public", template_folder="views")


################################################################################
# Home page reroute
################################################################################
@app.route("/")
def home():
    """Reroute home URL to license lookup form"""
    return redirect(url_for("license_page"))


################################################################################
# Licenses
################################################################################
LICENSE_CONTEXT = {
    "title": "Seattle Public Vehicle Lookup",
    "entities": [{"entity_name_short": "License (wildcard)", "query_param": "license"}],
    "data_source": "https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb",
    "lookup_url": "license",
}


@app.route("/license")
def license_page():
    """License lookup form render"""
    # Check for badge query params and load if it exists.
    license = request.args.get("license")
    html = dataset.license_lookup(license)

    # Return the basic lookup form if not
    return render_template("index.html", **LICENSE_CONTEXT, entity_html=html)


################################################################################
# Names
################################################################################
NAME_CONTEXT = {
    "title": "Seattle Officer Name Lookup",
    "entities": [
        {"entity_name_short": "First Name (wildcard)", "query_param": "first"},
        {"entity_name_short": "Last Name (wildcard)", "query_param": "last"},
        {"entity_name_short": "Badge Number", "query_param": "badge"},
    ],
    "data_source": "https://data.seattle.gov/City-Business/City-of-Seattle-Wage-Data/2khk-5ukd",
    "lookup_url": "name",
}


@app.route("/name")
def name_page():
    """Officer name lookup form render"""
    first_name = request.args.get("first")
    last_name = request.args.get("last")
    badge = request.args.get("badge")
    strict_search = request.args.get("strict_search")
    html = dataset.name_lookup(first_name, last_name, badge)

    return render_template(
        "index.html",
        **NAME_CONTEXT,
        entity_html=html,
        strict_search=strict_search,
    )


################################################################################
# Old compatibility endpoints
################################################################################
@app.route("/license-lookup/<license>")
def license_lookup(license):
    html = dataset.license_lookup(license)
    strict_search = request.args.get("strict_search")
    return render_template(
        "index.html",
        **LICENSE_CONTEXT,
        entity_html=html,
        strict_search=strict_search,
    )


@app.route("/badge-lookup/<badge>")
def badge_lookup(badge):
    html = dataset.name_lookup(None, None, badge)
    strict_search = request.args.get("strict_search")
    return render_template(
        "index.html",
        **NAME_CONTEXT,
        entity_html=html,
        strict_search=strict_search,
    )


@app.route("/name-lookup/<name>")
def name_lookup(name):
    html = dataset.name_lookup(name, None, None)
    strict_search = request.args.get("strict_search")
    return render_template(
        "index.html",
        **NAME_CONTEXT,
        entity_html=html,
        strict_search=strict_search,
    )


if __name__ == "__main__":
    app.run()
