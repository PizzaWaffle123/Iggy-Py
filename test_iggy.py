# IggyPy Testing Suite

import os
from dotenv import load_dotenv


def test_test_token_existence():
    load_dotenv()
    assert os.getenv("token_test") is not None


def test_main_token_existence():
    load_dotenv()
    assert os.getenv("token_main") is not None
