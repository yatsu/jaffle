#!/bin/sh -eu

pip install notebook==5.3.1 pytest

pip install -e .[dev]
