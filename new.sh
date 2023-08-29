#!/bin/bash
_CONDA_ROOT="/Users/williamhbelew/opt/anaconda3"
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
\. "$_CONDA_ROOT/etc/profile.d/conda.sh" || return $?
conda activate "43_practice_env"

python3 utils.py new