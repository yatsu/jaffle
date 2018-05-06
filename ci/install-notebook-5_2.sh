#!/bin/sh -eu

pip install notebook==5.2.2 pytest

pip install -e .[dev]
