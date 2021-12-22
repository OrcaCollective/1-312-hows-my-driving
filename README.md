# 1-312-hows-my-driving
Easy public vehicle lookup

## Description

This tool uses Seattle Government's public data API, located here: https://data.seattle.gov/City-Business/Active-Fleet-Complement/enxu-fgzb

Licenses are looked up in the dataset and if a vehicle is found, that data is displayed.

## Development

We use the [`just` command runner](https://github.com/casey/just), you'll need to install it before running any steps below.

### Build and run the app

Build the image with `just build` and run it using `just up`.
The server will be available at port `3030`.

To run this image in production, use the `IS_PROD` variable for any actions, e.g. `IS_PROD=true just up`.

### If you want to make changes

The flask server will detect any changes made to the code and restart the application to pick up said changes.

To run the static checks (`just lint`), you will first need to [install `pre-commit`](https://pre-commit.com/).
