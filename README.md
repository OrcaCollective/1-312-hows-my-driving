# 1-312-hows-my-driving
Easy public vehicle lookup

## Description

This tool uses Seattle Government's public data API, located here: https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb

Licenses are looked up in the dataset and if a vehicle is found, that data is displayed.

## Development

Build the image with `docker build -t <tag> .`. Run it with `docker run -p 5000:5000 <tag>`.
