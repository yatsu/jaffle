#!/bin/sh -eu

pip install notebook==5.0.0 pytest
pip install -r $@

pip install -e .
