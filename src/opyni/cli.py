import logging
import sys

import simple_parsing
import argparse

import opyni.configuration as config

from opyni.generator import run_opyni


def _setup_logging(verbosity: int) -> None:  # noqa: FBT001
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    if verbosity >= 2:
        level = logging.DEBUG

    handler: logging.Handler = logging.StreamHandler()

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s]"
               "(%(name)s:%(funcName)s:%(lineno)d): %(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )


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


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    if len(argv) <= 1:
        argv.append("--help")

    argument_parser = _create_argument_parser()
    parsed = argument_parser.parse_args(argv)

    _setup_logging(parsed.verbosity)
    _set_configuration(parsed.config)

    return run_opyni()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
