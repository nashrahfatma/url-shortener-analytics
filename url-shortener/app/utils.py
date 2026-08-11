"""
utils.py
--------
Small helper functions kept separate from the main app logic
so they're easy to unit test in isolation (see tests/test_main.py).
"""

import random
import string

# Characters used to build short codes - alphanumeric, mixed case.
# Avoids ambiguous characters is a nice-to-have improvement you could
# mention in an interview (e.g. removing 0/O, 1/l/I).
_ALPHABET = string.ascii_letters + string.digits
_CODE_LENGTH = 6


def generate_short_code(length: int = _CODE_LENGTH) -> str:
    """
    Generates a random alphanumeric short code, e.g. 'aZ3kD9'.

    Using random generation (rather than an incrementing counter like
    1, 2, 3...) avoids exposing how many URLs the system has created,
    and makes codes harder to guess/enumerate.
    """
    return "".join(random.choices(_ALPHABET, k=length))
