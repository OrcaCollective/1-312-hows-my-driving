# 1-312-hows-my-driving
Easy public vehicle lookup

## Description

This tool uses Seattle Government's public data API, located here: https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb

Licenses are looked up in the dataset and if a vehicle is found, that data is displayed.

## Development

### If you just want to run the app

Build the image with `docker build -t <tag> .`. Run it with `docker run -p 5000:5000 <tag>`.

### If you want to make changes

1. Install a python virtual environment: `python3 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
4. Install the pre-commit hook: `pre-commit install`
5. Run the app: `cd src; FLASK_DEBUG=1 flask run`
6. Make changes and contribute 🙌
