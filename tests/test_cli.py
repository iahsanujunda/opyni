import os
from unittest.mock import patch, MagicMock

import pytest

from src.opyni.cli import main


@pytest.fixture(scope='module')
def mock_run_opyni():
    with patch('src.opyni.cli.run_opyni') as mock:
        yield mock


@patch.dict(os.environ, {}, clear=True)
def test_main_missing_env_var():
    assert main([]) == -1


@patch.dict(os.environ, {"OPENAI_API_KEY": "foobar"})
@patch("src.opyni.cli._setup_logging")
@patch("src.opyni.cli._create_argument_parser")
def test_main_with_arguments(mock_parser, _, mock_run_opyni):
    mock_run_opyni.return_value.value = 0

    parser = MagicMock()
    mock_parser.return_value = parser

    main(['opyni', '-vv'])
    mock_run_opyni.assert_called_once()
