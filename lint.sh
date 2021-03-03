#!/bin/bash
find .  -path ./venv -prune -false -o -name "*.py" -exec pylint --extension-pkg-whitelist='pydantic' {} +;
