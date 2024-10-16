#!/usr/bin/env bash

python -m venv .venv
. .venv/bin/activate
pip install pybuilder
pip install twine

pyb publish
if [ -z "$1" ]
then
    echo "No username supplied"
    exit 0
fi
if [ -z "$2" ]
then
    echo "No password supplied"
    exit 0
fi
twine upload  target/dist/core*/dist/core*.whl --repository-url https://$1:$2@nexus.ycappuccino.fr/simple/