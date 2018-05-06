#!/bin/sh -eu

pip install notebook==5.1.0 pytest

pip install -e .[dev]
