import logging
import sys

import simple_parsing
import argparse

from opyni.generator import run_opyni


def _setup_logging(verbosity: int) -> None:  # noqa: FBT001
    level = logging.WARNING
    if verbosity == 0:
        level = logging.INFO
    if verbosity >= 1:
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
        description="Opyni is an automatci unit test generator",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="verbose output (repeat for increased verbosity)",
    )
    parser.add_argument(
        "-f",
        "--input-file",
        action="count",
        dest="input_file",
        default="",
        help="Input file",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    if len(argv) <= 1:
        argv.append("--help")

    argument_parser = _create_argument_parser()
    parsed = argument_parser.parse_args(argv)

    _setup_logging(parsed.verbosity)

    return run_opyni(input_file=parsed.input_file)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
