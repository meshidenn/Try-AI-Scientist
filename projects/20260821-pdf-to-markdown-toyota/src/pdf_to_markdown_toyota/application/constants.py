"""application層で共有する評価定数。"""

from __future__ import annotations

import re


MODEL_NAME = "gemma4-26b-moe"
MODEL_ID = "google/gemma-4-26B-A4B-it"
NUMBER_PATTERN = re.compile(r"(?:[-+]?[0-9][0-9,]*(?:\.[0-9]+)?%?)")
N_VALUES = tuple(range(1, 11))
