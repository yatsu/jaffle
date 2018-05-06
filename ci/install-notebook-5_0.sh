#!/bin/sh -eu

pip install notebook==5.0.0 pytest

pip install -e .[dev]
