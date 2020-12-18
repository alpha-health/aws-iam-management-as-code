#!/usr/bin/env bash
set -o errexit
set -o pipefail

pushd py_scripts
python policy_generator.py
popd
./cloudformation_validation.sh