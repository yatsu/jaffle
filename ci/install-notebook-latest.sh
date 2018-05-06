#!/bin/sh -eu

pip install notebook pytest

pip install -e .[dev]
