import logging
import os
import sys

import simple_parsing
import argparse

from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import pprint

import opyni.configuration as config

from opyni.generator import run_opyni


def _setup_logging(verbosity: int) -> Console:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    if verbosity >= 2:
        level = logging.DEBUG

    console = Console(tab_size=4)
    handler = RichHandler(
        rich_tracebacks=True, log_time_format="[%X]", console=console
    )
    handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s]"
               "(%(name)s:%(funcName)s:%(lineno)d): %(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )
    return console


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = simple_parsing.ArgumentParser(
        add_option_string_dash_variants=simple_parsing.DashVariant.UNDERSCORE_AND_DASH,
        description="Opyni is an automatic unit test generator",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="verbose output (repeat for increased verbosity)",
    )
    parser.add_arguments(config.Configuration, dest="config")

    return parser


def _set_configuration(configuration: config.Configuration) -> None:
    config.configuration = configuration


_REQUIRED_ENV = "OPENAI_API_KEY"


def main(argv: list[str] | None = None) -> int:
    if _REQUIRED_ENV not in os.environ:
        pprint(
            f"""Environment variable '{_REQUIRED_ENV}' not set."""
        )
        return -1

    if argv is None:
        argv = sys.argv
    if len(argv) <= 1:
        argv.append("--help")

    argument_parser = _create_argument_parser()
    parsed = argument_parser.parse_args(argv[1:])
    console = _setup_logging(parsed.verbosity)
    _set_configuration(parsed.config)

    with console.status("Running Opyni...\n"):
        return run_opyni().value


if __name__ == "__main__":
    sys.exit(main(sys.argv))
