#!/bin/bash

pipenv install &&
pipenv run pybabel compile -D Deadline -d po
#pipenv run python -m Deadline.main
