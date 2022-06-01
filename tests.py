# IggyPy Testing Suite
"""
All tests are encompassed within the run_tests() function. It takes an integer level specifier, which defaults to 1.

0 - These tests run in all circumstances, and are tests of critical functionality. The bot WILL NOT RUN if these tests
do not pass.

1 - Important tests not required for bot operation.

2 - Additional tests.

3 - Advanced tests.
"""

import os.path


def run_tests(level=1):

    if level < 0:
        level = 0
    if level > 3:
        level = 3

    match level:
        case 0:
            level_designator = "BASIC"
        case 2:
            level_designator = "EXTRA"
        case 3:
            level_designator = "ALL"
        case _:
            level_designator = "STANDARD"

    print("Running tests of designation: %s" % level_designator)
    print("---")

    total_tests = 0
    tests_performed = 0

    # --------------------------------------------
    # Token Existence Test
    # Checks that the current directory contains either token_test.txt or token_main.txt
    # Level: BASIC
    total_tests += 1
    if level >= 0:
        tests_performed += 1
        print("TEST #%d (TOKEN EXISTENCE)" % total_tests)
        if os.path.isfile("./token_test.txt") and os.path.isfile("./token_main.txt"):
            print("Found both tokens. Success.")
        elif os.path.isfile("./token_test.txt"):
            print("Found test token. Success.")
        elif os.path.ifile("./token_main.txt"):
            print("Found main token. Success.")
        else:
            print("No tokens found. Failure.")
            print("---")
            return False
    # --------------------------------------------
    print("---")
    print("All tests passed.")
    print("(%d tests excluded due to testing level.)" % (total_tests - tests_performed))
    return True


if __name__ == "__main__":
    test_result = run_tests(3)

