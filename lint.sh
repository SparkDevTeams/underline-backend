#!/bin/bash
find . -name "*.py" -exec pylint --extension-pkg-whitelist='pydantic' {} +;
